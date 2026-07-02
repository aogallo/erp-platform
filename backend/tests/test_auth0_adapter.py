from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.auth.adapters.auth0 import Auth0AuthProvider, Auth0ProviderConfig
from shared.auth.contracts import TokenValidationResult


class FakeOidcProvider:
    def __init__(self) -> None:
        self.tokens: list[str] = []

    async def validate_access_token(
        self, token: str, *, now: datetime | None = None
    ) -> TokenValidationResult:
        self.tokens.append(token)
        issued_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
        return TokenValidationResult(
            provider_subject="auth0|subject-10",
            issuer="https://tenant.auth0.com/",
            audience="https://api.erp.test",
            issued_at=issued_at,
            expires_at=issued_at + timedelta(minutes=15),
            email="admin@acme.test",
            claims={"scope": "openid profile email"},
        )


def test_auth0_config_derives_oidc_issuer_and_jwks_url() -> None:
    config = Auth0ProviderConfig(
        domain="tenant.auth0.com",
        audience="https://api.erp.test",
    )

    oidc_config = config.to_oidc_config()

    assert oidc_config.issuer == "https://tenant.auth0.com/"
    assert oidc_config.audience == "https://api.erp.test"
    assert oidc_config.jwks_url == "https://tenant.auth0.com/.well-known/jwks.json"


@pytest.mark.asyncio
async def test_auth0_provider_delegates_token_validation_to_oidc_provider() -> None:
    oidc_provider = FakeOidcProvider()
    provider = Auth0AuthProvider(oidc_provider=oidc_provider)

    result = await provider.validate_access_token("auth0-access-token")

    assert oidc_provider.tokens == ["auth0-access-token"]
    assert result.provider_subject == "auth0|subject-10"
    assert result.claims == {"scope": "openid profile email"}


def test_auth0_provider_uses_no_provider_sdk_in_domain_boundary() -> None:
    config = Auth0ProviderConfig(
        domain="tenant.auth0.com",
        audience="https://api.erp.test",
    )

    provider = Auth0AuthProvider.from_config(config)

    assert provider.sdk_module_name is None
