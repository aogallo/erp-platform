from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from shared.auth.adapters.oidc import OidcAuthProvider, OidcProviderConfig


class FakeTokenVerifier:
    def __init__(self, claims: dict[str, Any] | None = None) -> None:
        self.claims = claims or {}
        self.calls: list[tuple[str, OidcProviderConfig]] = []

    def verify(self, token: str, config: OidcProviderConfig) -> dict[str, Any]:
        self.calls.append((token, config))
        if token == "bad-signature-token":
            raise PermissionError("Invalid token signature")
        return self.claims


def valid_claims(**overrides: Any) -> dict[str, Any]:
    issued_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    claims: dict[str, Any] = {
        "sub": "auth0|subject-10",
        "iss": "https://tenant.auth0.com/",
        "aud": "https://api.erp.test",
        "iat": int(issued_at.timestamp()),
        "exp": int((issued_at + timedelta(minutes=15)).timestamp()),
        "email": "admin@acme.test",
        "roles": ["admin"],
    }
    claims.update(overrides)
    return claims


def make_provider(claims: dict[str, Any]) -> OidcAuthProvider:
    return OidcAuthProvider(
        config=OidcProviderConfig(
            issuer="https://tenant.auth0.com/",
            audience="https://api.erp.test",
            jwks_url="https://tenant.auth0.com/.well-known/jwks.json",
        ),
        token_verifier=FakeTokenVerifier(claims),
    )


@pytest.mark.asyncio
async def test_oidc_provider_validates_token_and_extracts_claims() -> None:
    provider = make_provider(valid_claims())

    result = await provider.validate_access_token(
        "valid-access-token", now=datetime(2026, 7, 1, 12, 1, tzinfo=UTC)
    )

    assert result.provider_subject == "auth0|subject-10"
    assert result.issuer == "https://tenant.auth0.com/"
    assert result.audience == "https://api.erp.test"
    assert result.email == "admin@acme.test"
    assert result.claims["roles"] == ["admin"]
    assert result.issued_at == datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    assert result.expires_at == datetime(2026, 7, 1, 12, 15, tzinfo=UTC)


@pytest.mark.asyncio
async def test_oidc_provider_rejects_wrong_issuer() -> None:
    provider = make_provider(valid_claims(iss="https://evil.example/"))

    with pytest.raises(PermissionError, match="Invalid token issuer"):
        await provider.validate_access_token("valid-access-token")


@pytest.mark.asyncio
async def test_oidc_provider_rejects_wrong_audience() -> None:
    provider = make_provider(valid_claims(aud="https://other-api.example"))

    with pytest.raises(PermissionError, match="Invalid token audience"):
        await provider.validate_access_token("valid-access-token")


@pytest.mark.asyncio
async def test_oidc_provider_rejects_invalid_signature() -> None:
    provider = make_provider(valid_claims())

    with pytest.raises(PermissionError, match="Invalid token signature"):
        await provider.validate_access_token("bad-signature-token")


@pytest.mark.asyncio
async def test_oidc_provider_rejects_expired_token() -> None:
    expired_at = datetime(2026, 6, 30, 12, 0, tzinfo=UTC)
    provider = make_provider(valid_claims(exp=int(expired_at.timestamp())))

    with pytest.raises(PermissionError, match="Token is expired"):
        await provider.validate_access_token(
            "valid-access-token",
            now=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        )
