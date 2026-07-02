from pytest import MonkeyPatch

from shared.config import Settings


def test_auth_settings_have_safe_defaults() -> None:
    settings = Settings()

    assert settings.auth_issuer == ""
    assert settings.auth_audience == ""
    assert settings.auth_jwks_url == ""
    assert settings.auth_session_max_age_minutes == 480
    assert settings.auth_session_idle_timeout_minutes == 60
    assert settings.auth_session_revocation_required is True


def test_auth_settings_read_oidc_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ERP_AUTH_ISSUER", "https://tenant.auth0.com/")
    monkeypatch.setenv("ERP_AUTH_AUDIENCE", "https://api.erp.test")
    monkeypatch.setenv("ERP_AUTH_JWKS_URL", "https://tenant.auth0.com/.well-known/jwks.json")
    monkeypatch.setenv("ERP_AUTH_SESSION_MAX_AGE_MINUTES", "30")
    monkeypatch.setenv("ERP_AUTH_SESSION_IDLE_TIMEOUT_MINUTES", "10")
    monkeypatch.setenv("ERP_AUTH_SESSION_REVOCATION_REQUIRED", "false")

    settings = Settings.from_env()

    assert settings.auth_issuer == "https://tenant.auth0.com/"
    assert settings.auth_audience == "https://api.erp.test"
    assert settings.auth_jwks_url == "https://tenant.auth0.com/.well-known/jwks.json"
    assert settings.auth_session_max_age_minutes == 30
    assert settings.auth_session_idle_timeout_minutes == 10
    assert settings.auth_session_revocation_required is False
