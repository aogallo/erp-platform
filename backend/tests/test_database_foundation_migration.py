from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = PROJECT_ROOT / "backend/migrations/sql/V1__database_foundation.sql"
FLYWAY_CONFIG_PATH = PROJECT_ROOT / "backend/flyway.conf"
EXPECTED_CONTEXT_SCHEMAS = {
    "iam",
    "crm",
    "sales",
    "inventory",
    "purchasing",
    "accounting",
    "banking",
    "hr",
}


def _migration_sql() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def _flyway_config() -> str:
    return FLYWAY_CONFIG_PATH.read_text(encoding="utf-8")


def test_database_foundation_migration_enables_pgcrypto() -> None:
    sql = _migration_sql()

    assert re.search(
        r"create\s+extension\s+if\s+not\s+exists\s+pgcrypto\b",
        sql,
        flags=re.IGNORECASE,
    )


def test_database_foundation_migration_creates_only_context_schemas() -> None:
    sql = _migration_sql()

    created_schemas = set(
        re.findall(
            r"create\s+schema\s+if\s+not\s+exists\s+([a-z_][a-z0-9_]*)\b",
            sql,
            flags=re.IGNORECASE,
        )
    )

    assert created_schemas == EXPECTED_CONTEXT_SCHEMAS


def test_database_foundation_migration_creates_no_business_tables() -> None:
    sql = _migration_sql()

    assert not re.search(r"\bcreate\s+table\b", sql, flags=re.IGNORECASE)


def test_flyway_config_uses_explicit_database_environment_variables() -> None:
    config = _flyway_config()

    assert (
        "flyway.url=jdbc:postgresql://"
        "${env.ERP_DATABASE_HOST}:${env.ERP_DATABASE_PORT}/${env.ERP_DATABASE_NAME}"
        in config
    )
    assert "flyway.user=${env.ERP_DATABASE_USER}" in config
    assert "flyway.password=${env.ERP_DATABASE_PASSWORD}" in config
    assert "${databaseHost}" not in config
    assert "${databasePort}" not in config
    assert "${databaseName}" not in config
    assert "${databaseUser}" not in config
    assert "${databasePassword}" not in config
