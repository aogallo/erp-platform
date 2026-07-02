"""Auth0-specific adapter configuration over the generic OIDC boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from shared.auth.adapters.oidc import OidcAuthProvider, OidcProviderConfig
from shared.auth.contracts import TokenValidationResult


class OidcValidationProvider(Protocol):
    """Minimal OIDC validation behavior used by the Auth0 wrapper."""

    async def validate_access_token(
        self, token: str, *, now: datetime | None = None
    ) -> TokenValidationResult:
        """Validate a bearer access token and return provider claims."""


@dataclass(frozen=True)
class Auth0ProviderConfig:
    """Auth0 tenant settings used to derive provider-neutral OIDC config."""

    domain: str
    audience: str

    def to_oidc_config(self) -> OidcProviderConfig:
        normalized_domain = self.domain.removeprefix("https://").rstrip("/")
        issuer = f"https://{normalized_domain}/"
        return OidcProviderConfig(
            issuer=issuer,
            audience=self.audience,
            jwks_url=f"{issuer}.well-known/jwks.json",
        )


class Auth0AuthProvider:
    """Thin Auth0 wrapper that delegates validation to the OIDC adapter."""

    sdk_module_name: None = None

    def __init__(self, *, oidc_provider: OidcValidationProvider) -> None:
        self._oidc_provider = oidc_provider

    @classmethod
    def from_config(cls, config: Auth0ProviderConfig) -> Auth0AuthProvider:
        return cls(oidc_provider=OidcAuthProvider(config=config.to_oidc_config()))

    async def validate_access_token(
        self, token: str, *, now: datetime | None = None
    ) -> TokenValidationResult:
        return await self._oidc_provider.validate_access_token(token, now=now)
