from contextlib import asynccontextmanager
# contextlib used to create a lifespan context manager for FastAPI applications
# allowing for setup and teardown of resources during the application's lifecycle.

import httpx
from fastapi import FastAPI

from app.config.settings import settings
from app.core.security.jwt_validator import JWTValidator


@asynccontextmanager  # this decorator allows the function to be used as an asynchronous context manager, enabling the use of 'async with' statements.
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient()

    try:
        jwt_validator = JWTValidator(
            http_client=http_client,
            issuer=settings.keycloak_issuer,
            jwks_url=settings.keycloak_jwks_url,
            audience=settings.keycloak_api_audience,
            cache_ttl_seconds=settings.jwt_jwks_cache_ttl_seconds,
            unknown_kid_refresh_interval_seconds=(
                settings.jwt_unknown_kid_refresh_interval_seconds
            ),
        )

        app.state.jwt_validator = jwt_validator

        yield

    finally:
        await http_client.aclose()
