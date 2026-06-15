from pathlib import Path

from main import create_app
from pytest import MonkeyPatch
from fastapi.testclient import TestClient
from shared.config import Settings, get_settings


def test_backend_import_exposes_application_factory() -> None:
    app = create_app()

    assert app.title == "ERP Platform API"
    assert app.version == "0.1.0"


def test_bounded_context_routes_are_registered_with_scaffold_behavior() -> None:
    app = create_app()
    client = TestClient(app)

    customer_response = client.get("/crm/customers")
    invoice_response = client.get("/sales/invoices")
    organizational_units_response = client.get("/hr/organizational-units")
    positions_response = client.get("/hr/positions")

    assert customer_response.status_code == 501
    assert customer_response.json() == {
        "detail": "CRM customer endpoint scaffold is registered but not implemented."
    }
    assert invoice_response.status_code == 501
    assert invoice_response.json() == {
        "detail": "Sales invoice endpoint scaffold is registered but not implemented."
    }
    assert organizational_units_response.status_code == 501
    assert organizational_units_response.json() == {
        "detail": (
            "HR organizational unit endpoint scaffold is registered but not "
            "implemented."
        )
    }
    assert positions_response.status_code == 501
    assert positions_response.json() == {
        "detail": "HR position endpoint scaffold is registered but not implemented."
    }


def test_backend_settings_read_postgres_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ERP_DATABASE_HOST", "db")
    monkeypatch.setenv("ERP_DATABASE_PORT", "5433")
    monkeypatch.setenv("ERP_DATABASE_NAME", "erp_test")
    monkeypatch.setenv("ERP_DATABASE_USER", "erp_user")
    monkeypatch.setenv("ERP_DATABASE_PASSWORD", "secret")

    settings = Settings.from_env()

    assert settings.database_url == (
        "postgresql+psycopg://erp_user:secret@db:5433/erp_test"
    )
    assert get_settings().app_name == "ERP Platform API"


def test_backend_settings_load_dotenv_file(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "ERP_DATABASE_HOST=dotenv-db\n"
        "ERP_DATABASE_PORT=5440\n"
        "ERP_DATABASE_NAME=erp_platform_test\n"
        "ERP_DATABASE_USER=dotenv_user\n"
        "ERP_DATABASE_PASSWORD=dotenv_secret\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    settings = Settings.from_env()

    assert settings.database_url == (
        "postgresql+psycopg://dotenv_user:dotenv_secret"
        "@dotenv-db:5440/erp_platform_test"
    )
