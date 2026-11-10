import asyncio
import json
import logging
import time
from typing import Any

import httpx
import jwt
from jwt.algorithms import RSAAlgorithm

logger = logging.getLogger(__name__)

ALLOWED_ALGORITHM = "RS256"


class JWTValidationError(Exception):
    """Raised when a JWT is invalid or cannot be trusted."""


class JWKSUnavailableError(Exception):
    """Raised when trusted JWKS data cannot be retrieved or processed."""


class JWTValidator:
    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        jwks_url: str,
        issuer: str,
        audience: str,
        cache_ttl_seconds: int = 300,
        unknown_kid_refresh_interval_seconds: int = 30,
    ) -> None:
        if cache_ttl_seconds <= 0:
            raise ValueError("JWKS cache TTL must be greater than zero.")

        if unknown_kid_refresh_interval_seconds <= 0:
            raise ValueError("Unknown key refresh interval must be greater than zero.")

        self.http_client = http_client
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.audience = audience
        self.cache_ttl_seconds = cache_ttl_seconds
        self.unknown_kid_refresh_interval_seconds = unknown_kid_refresh_interval_seconds

        self._signing_keys: dict[str, Any] = {}
        self._cache_expires_at = 0.0
        self._last_unknown_kid_refresh_at = 0.0
        self._refresh_lock = asyncio.Lock()

    async def validate_token(self, token: str) -> dict[str, Any]:
        if not token:
            raise JWTValidationError("Token is missing.")

        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise JWTValidationError("Malformed JWT header.") from exc

        algorithm = header.get("alg")
        key_id = header.get("kid")

        if algorithm != ALLOWED_ALGORITHM:
            raise JWTValidationError("Unsupported JWT signing algorithm.")

        if not isinstance(key_id, str) or not key_id:
            raise JWTValidationError("JWT header is missing a valid key ID.")

        signing_key = await self._get_signing_key(key_id)

        try:
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=[ALLOWED_ALGORITHM],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "require": ["exp", "iss", "aud", "sub"],
                    "verify_nbf": True,
                },
            )
        except jwt.PyJWTError as exc:
            raise JWTValidationError("JWT validation failed.") from exc

        subject = claims.get("sub")

        if not isinstance(subject, str) or not subject.strip():
            raise JWTValidationError("JWT subject is missing or invalid.")

        return claims

    async def _get_signing_key(self, key_id: str) -> Any:
        now = time.monotonic()
        cache_is_valid = now < self._cache_expires_at

        if cache_is_valid and key_id in self._signing_keys:
            return self._signing_keys[key_id]

        async with self._refresh_lock:
            now = time.monotonic()
            cache_is_valid = now < self._cache_expires_at

            if cache_is_valid and key_id in self._signing_keys:
                return self._signing_keys[key_id]

            if cache_is_valid:
                cooldown_elapsed = (
                    now - self._last_unknown_kid_refresh_at
                    >= self.unknown_kid_refresh_interval_seconds
                )

                if not cooldown_elapsed:
                    raise JWTValidationError("JWT signing key was not found.")

                self._last_unknown_kid_refresh_at = now

            await self._refresh_jwks()

            signing_key = self._signing_keys.get(key_id)

            if signing_key is None:
                raise JWTValidationError("JWT signing key was not found.")

            return signing_key

    async def _refresh_jwks(self) -> None:
        try:
            response = await self.http_client.get(self.jwks_url)
            response.raise_for_status()
            jwks_document = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.exception("Failed to retrieve Keycloak JWKS.")
            raise JWKSUnavailableError(
                "Unable to retrieve trusted signing keys."
            ) from exc

        if not isinstance(jwks_document, dict):
            raise JWKSUnavailableError("Invalid JWKS document.")

        jwks_keys = jwks_document.get("keys")

        if not isinstance(jwks_keys, list):
            raise JWKSUnavailableError("JWKS document has no valid keys list.")

        signing_keys: dict[str, Any] = {}

        try:
            for jwk_data in jwks_keys:
                if not isinstance(jwk_data, dict):
                    continue

                key_id = jwk_data.get("kid")

                if (
                    jwk_data.get("kty") != "RSA"
                    or jwk_data.get("use", "sig") != "sig"
                    or jwk_data.get("alg", ALLOWED_ALGORITHM) != ALLOWED_ALGORITHM
                    or not isinstance(key_id, str)
                    or not key_id
                ):
                    continue

                signing_keys[key_id] = RSAAlgorithm.from_jwk(json.dumps(jwk_data))

        except (ValueError, TypeError, KeyError, jwt.PyJWTError) as exc:
            raise JWKSUnavailableError(
                "Unable to process Keycloak signing keys."
            ) from exc

        if not signing_keys:
            raise JWKSUnavailableError(
                "JWKS document contains no usable RSA signing keys."
            )

        self._signing_keys = signing_keys
        self._cache_expires_at = time.monotonic() + self.cache_ttl_seconds
