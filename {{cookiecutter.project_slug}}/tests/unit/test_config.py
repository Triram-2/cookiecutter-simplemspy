from {{cookiecutter.python_package_name}}.core.config import LogSettings, AppSettings, BASE_DIR, DATA_DIR


def test_log_settings_instantiation():
    log_settings = LogSettings()
    assert log_settings.path == BASE_DIR / "logs"
    assert (BASE_DIR / "logs").exists()  # Check directory creation
    assert log_settings.console_level == "INFO"




def test_app_settings_instantiation(monkeypatch):
    # Prevent modification of actual .env for tests if loaded
    monkeypatch.setenv("APP_APP_ENV", "test")  # Respect env_prefix
    app_settings = AppSettings()
    assert app_settings.app_env == "test"
    assert app_settings.log is not None
    assert app_settings.app_host == "0.0.0.0"


def test_data_dir_creation():
    _ = AppSettings()  # Instantiation should trigger dir creation
    assert DATA_DIR.exists()
