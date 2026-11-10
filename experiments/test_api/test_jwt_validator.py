import asyncio
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from app.core.security.jwt_validator import (
    JWTValidationError,
    JWTValidator,
    JWKSUnavailableError,
)


JWKS_URL = "https://keycloak.example.com/realms/platform/protocol/openid-connect/certs"
ISSUER = "https://keycloak.example.com/realms/platform"
AUDIENCE = "platform-api"


@pytest.fixture
def private_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


@pytest.fixture
def jwks_document(private_key):
    public_key = private_key.public_key()

    jwk_data = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk_data.update(
        {
            "kid": "test-key-1",
            "use": "sig",
            "alg": "RS256",
        }
    )

    return {"keys": [jwk_data]}


@pytest.fixture
def http_client(jwks_document):
    client = AsyncMock(spec=httpx.AsyncClient)

    response = httpx.Response(
        200,
        json=jwks_document,
        request=httpx.Request("GET", JWKS_URL),
    )

    client.get.return_value = response

    return client


@pytest.fixture
def validator(http_client):
    return JWTValidator(
        http_client=http_client,
        jwks_url=JWKS_URL,
        issuer=ISSUER,
        audience=AUDIENCE,
    )


def create_token(
    private_key,
    *,
    subject="user-123",
    issuer=ISSUER,
    audience=AUDIENCE,
    expires_at=None,
    not_before=None,
    key_id="test-key-1",
):
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "exp": expires_at or now + timedelta(minutes=5),
    }

    if not_before is not None:
        payload["nbf"] = not_before

    return jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"kid": key_id},
    )


@pytest.mark.asyncio
async def test_validate_token_accepts_valid_token(
    validator,
    private_key,
    http_client,
):
    token = create_token(private_key)

    claims = await validator.validate_token(token)

    assert claims["sub"] == "user-123"
    assert claims["iss"] == ISSUER
    assert claims["aud"] == AUDIENCE

    http_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_token_rejects_invalid_signature(
    validator,
):
    attacker_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    token = create_token(attacker_key)

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_expired_token(
    validator,
    private_key,
):
    token = create_token(
        private_key,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_wrong_issuer(
    validator,
    private_key,
):
    token = create_token(
        private_key,
        issuer="https://untrusted.example.com/realms/other",
    )

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_wrong_audience(
    validator,
    private_key,
):
    token = create_token(
        private_key,
        audience="another-api",
    )

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_future_not_before(
    validator,
    private_key,
):
    token = create_token(
        private_key,
        not_before=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_empty_subject(
    validator,
    private_key,
):
    token = create_token(private_key, subject="")

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_missing_subject(
    validator,
    private_key,
):
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key-1"},
    )

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_unsupported_algorithm(
    validator,
):
    token = jwt.encode(
        {"sub": "user-123"},
        "test-secret-for-unsupported-algorithm-32-bytes",
        algorithm="HS256",
        headers={"kid": "test-key-1"},
    )

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_malformed_token(
    validator,
):
    with pytest.raises(JWTValidationError):
        await validator.validate_token("this-is-not-a-jwt")


@pytest.mark.asyncio
async def test_validate_token_rejects_missing_key_id(
    validator,
    private_key,
):
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "user-123",
            "iss": ISSUER,
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
    )

    with pytest.raises(JWTValidationError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_reuses_cached_jwks(
    validator,
    private_key,
    http_client,
):
    first_token = create_token(private_key)
    second_token = create_token(private_key)

    await validator.validate_token(first_token)
    await validator.validate_token(second_token)

    http_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_token_refreshes_jwks_for_unknown_key(
    validator,
    private_key,
    http_client,
):
    first_token = create_token(private_key)
    unknown_key_token = create_token(
        private_key,
        key_id="unknown-key",
    )

    await validator.validate_token(first_token)

    with pytest.raises(JWTValidationError):
        await validator.validate_token(unknown_key_token)

    assert http_client.get.await_count == 2


@pytest.mark.asyncio
async def test_validate_token_raises_when_jwks_is_unavailable(
    validator,
    http_client,
    private_key,
):
    response = httpx.Response(
        503,
        request=httpx.Request("GET", JWKS_URL),
    )
    http_client.get.return_value = response

    token = create_token(private_key)

    with pytest.raises(JWKSUnavailableError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_rejects_empty_jwks(
    validator,
    http_client,
    private_key,
):
    response = httpx.Response(
        200,
        json={"keys": []},
        request=httpx.Request("GET", JWKS_URL),
    )
    http_client.get.return_value = response

    token = create_token(private_key)

    with pytest.raises(JWKSUnavailableError):
        await validator.validate_token(token)


# Security hardening tests


@pytest.mark.asyncio
async def test_concurrent_requests_share_jwks_refresh(
    validator,
    private_key,
    http_client,
):
    token = create_token(private_key)

    results = await asyncio.gather(
        *[validator.validate_token(token) for _ in range(10)]
    )

    assert len(results) == 10
    assert all(result["sub"] == "user-123" for result in results)

    http_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_repeated_unknown_key_does_not_repeat_jwks_refresh(
    validator,
    private_key,
    http_client,
):
    valid_token = create_token(private_key)
    unknown_key_token = create_token(
        private_key,
        key_id="unknown-key",
    )

    await validator.validate_token(valid_token)

    for _ in range(3):
        with pytest.raises(JWTValidationError):
            await validator.validate_token(unknown_key_token)

    assert http_client.get.await_count == 2


@pytest.mark.asyncio
async def test_validate_token_rejects_malformed_rsa_jwk(
    validator,
    http_client,
    private_key,
):
    malformed_jwk = {
        "kid": "malformed-key",
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "e": "AQAB",
    }

    response = httpx.Response(
        200,
        json={"keys": [malformed_jwk]},
        request=httpx.Request("GET", JWKS_URL),
    )
    http_client.get.return_value = response

    token = create_token(private_key)

    with pytest.raises(JWKSUnavailableError):
        await validator.validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_does_not_use_expired_cache_during_jwks_outage(
    validator,
    http_client,
    private_key,
):
    token = create_token(private_key)

    # First request successfully loads the public key.
    await validator.validate_token(token)

    # Simulate expiration of the cached JWKS document.
    validator._cache_expires_at = 0.0

    # Keycloak becomes unavailable.
    http_client.get.return_value = httpx.Response(
        503,
        request=httpx.Request("GET", JWKS_URL),
    )

    with pytest.raises(JWKSUnavailableError):
        await validator.validate_token(token)

    assert http_client.get.await_count == 2
