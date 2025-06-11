from pydantic import PostgresDsn

from my_awesome_project.core.config import LogSettings, DBSettings, AppSettings, BASE_DIR, DATA_DIR


def test_log_settings_instantiation():
    log_settings = LogSettings()
    assert log_settings.path == BASE_DIR / "logs"
    assert (BASE_DIR / "logs").exists()  # Check directory creation
    assert log_settings.console_level == "INFO"


def test_db_settings_default_sqlite():
    db_settings = DBSettings(type="SQLITE")
    sqlite_file_path = DATA_DIR / "db" / "main.sqlite"
    assert db_settings.sqlite_file == sqlite_file_path
    expected_url = f"sqlite+aiosqlite:///{sqlite_file_path.resolve()}"
    validated_settings = DBSettings(type="SQLITE", sqlite_file=db_settings.sqlite_file)
    assert validated_settings.assembled_database_url == expected_url
    assert sqlite_file_path.parent.exists()  # Check directory creation


def test_db_settings_postgres():
    db_settings_data = {
        "type": "POSTGRESQL",
        "user": "testuser",
        "password": "testpassword",
        "host": "testhost",
        "port": 5433,
        "name": "testdb",
    }
    validated_settings = DBSettings(**db_settings_data)  # Validation happens here
    expected_url = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        username="testuser",
        password="testpassword",
        host="testhost",
        port=5433,
        path="/testdb",
    )
    assert validated_settings.assembled_database_url == expected_url


def test_db_settings_override_memory_sqlite():
    # Test with the alias
    db_settings = DBSettings(DATABASE_URL="sqlite+aiosqlite:///:memory:")
    assert db_settings.assembled_database_url == "sqlite+aiosqlite:///:memory:"


def test_db_settings_override_postgres_url():
    override_url = "postgresql+asyncpg://user:pass@host:1234/dbname"
    # Test with the alias
    db_settings = DBSettings(DATABASE_URL=override_url)
    assert db_settings.assembled_database_url == override_url


def test_app_settings_instantiation(monkeypatch):
    # Prevent modification of actual .env for tests if loaded
    monkeypatch.setenv("APP_APP_ENV", "test")  # Respect env_prefix
    app_settings = AppSettings()
    assert app_settings.app_env == "test"
    assert app_settings.db is not None
    assert app_settings.log is not None
    assert app_settings.app_host == "0.0.0.0"
    assert app_settings.db.assembled_database_url is not None


def test_data_dir_creation():
    _ = AppSettings()  # Instantiation should trigger dir creation via DBSettings
    assert DATA_DIR.exists()
    assert (DATA_DIR / "db").exists()
