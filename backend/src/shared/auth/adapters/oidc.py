"""Provider-neutral OIDC access-token validation skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from shared.auth.contracts import Principal, TokenValidationResult, require_permission


@dataclass(frozen=True)
class OidcProviderConfig:
    """Configuration required to validate an OIDC access token."""

    issuer: str
    audience: str
    jwks_url: str


class OidcTokenVerifier(Protocol):
    """Cryptographic JWT/JWKS verifier used behind the OIDC boundary."""

    def verify(self, token: str, config: OidcProviderConfig) -> dict[str, Any]:
        """Return verified JWT claims or raise when validation fails."""


class UnconfiguredOidcTokenVerifier:
    """Import-safe placeholder until a JWT library adapter is wired."""

    def verify(self, token: str, config: OidcProviderConfig) -> dict[str, Any]:
        raise NotImplementedError("OIDC token verifier is not wired yet")


class OidcAuthProvider:
    """Provider-neutral OIDC adapter for access-token validation."""

    def __init__(
        self,
        *,
        config: OidcProviderConfig,
        token_verifier: OidcTokenVerifier | None = None,
    ) -> None:
        self._config = config
        self._token_verifier = token_verifier or UnconfiguredOidcTokenVerifier()

    @property
    def config(self) -> OidcProviderConfig:
        return self._config

    async def validate_access_token(
        self, token: str, *, now: datetime | None = None
    ) -> TokenValidationResult:
        """Validate issuer, audience, signature, expiry, and extract claims."""

        claims = self._token_verifier.verify(token, self._config)
        self._validate_issuer(claims)
        self._validate_audience(claims)

        issued_at = self._timestamp_claim(claims, "iat")
        expires_at = self._timestamp_claim(claims, "exp")
        current_time = now or datetime.now(UTC)
        if expires_at <= current_time:
            raise PermissionError("Token is expired")

        provider_subject = self._string_claim(claims, "sub")
        return TokenValidationResult(
            provider_subject=provider_subject,
            issuer=self._config.issuer,
            audience=self._config.audience,
            issued_at=issued_at,
            expires_at=expires_at,
            email=self._optional_string_claim(claims, "email"),
            claims=dict(claims),
        )

    async def principal_from_bearer(
        self, token: str, tenant_id: str | None = None
    ) -> Principal:
        """Validate a token before local IAM policy builds a principal."""

        await self.validate_access_token(token)
        raise NotImplementedError("Local IAM principal resolution is not wired yet")

    def require_permission(self, principal: Principal, permission: str) -> None:
        require_permission(principal, permission)

    def _validate_issuer(self, claims: dict[str, Any]) -> None:
        if claims.get("iss") != self._config.issuer:
            raise PermissionError("Invalid token issuer")

    def _validate_audience(self, claims: dict[str, Any]) -> None:
        audience = claims.get("aud")
        if isinstance(audience, str):
            valid = audience == self._config.audience
        elif isinstance(audience, list):
            valid = self._config.audience in audience
        else:
            valid = False
        if not valid:
            raise PermissionError("Invalid token audience")

    def _timestamp_claim(self, claims: dict[str, Any], name: str) -> datetime:
        value = claims.get(name)
        if not isinstance(value, int):
            raise PermissionError(f"Missing or invalid token {name} claim")
        return datetime.fromtimestamp(value, tz=UTC)

    def _string_claim(self, claims: dict[str, Any], name: str) -> str:
        value = claims.get(name)
        if not isinstance(value, str) or value == "":
            raise PermissionError(f"Missing or invalid token {name} claim")
        return value

    def _optional_string_claim(self, claims: dict[str, Any], name: str) -> str | None:
        value = claims.get(name)
        if value is None:
            return None
        if not isinstance(value, str):
            raise PermissionError(f"Invalid token {name} claim")
        return value
