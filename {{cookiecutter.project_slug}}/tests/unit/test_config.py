from {{cookiecutter.python_package_name}}.core.config import LogSettings, AppSettings, BASE_DIR, DATA_DIR


def test_log_settings_instantiation():
    log_settings = LogSettings()
    assert log_settings.path == DATA_DIR / "logs"
    assert (DATA_DIR / "logs").exists()  # Check directory creation
    assert log_settings.console_level == "INFO"
    assert log_settings.loki_endpoint.startswith("http")


def test_log_settings_env_override(monkeypatch):
    monkeypatch.setenv("LOG_CONSOLE_LEVEL", "WARNING")
    log_settings = LogSettings()
    assert log_settings.console_level == "WARNING"




def test_app_settings_instantiation(monkeypatch):
    # Prevent modification of actual .env for tests if loaded
    monkeypatch.setenv("APP_APP_ENV", "test")  # Respect env_prefix
    app_settings = AppSettings()
    assert app_settings.app_env == "test"
    assert app_settings.log is not None
    assert app_settings.app_host == "0.0.0.0"


def test_app_settings_port_env(monkeypatch):
    monkeypatch.setenv("APP_APP_PORT", "1234")
    settings_override = AppSettings()
    assert settings_override.app_port == 1234


def test_data_dir_creation():
    _ = AppSettings()  # Instantiation should trigger dir creation
    assert DATA_DIR.exists()


def test_redis_settings_defaults():
    settings = AppSettings()
    redis = settings.redis
    assert redis.url.startswith("redis://")
    assert redis.stream_name == "{{cookiecutter.redis_stream_name}}"
    assert redis.consumer_group == "{{cookiecutter.redis_consumer_group}}"
    assert redis.consumer_name == "{{cookiecutter.redis_consumer_name}}"


def test_redis_settings_env_override(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://example.com:6379/1")
    cfg = AppSettings()
    assert cfg.redis.url == "redis://example.com:6379/1"


def test_statsd_defaults():
    cfg = AppSettings()
    assert cfg.statsd.host == "statsd"
    assert cfg.statsd.port == 8125


def test_jaeger_defaults():
    cfg = AppSettings()
    assert cfg.jaeger.host == "jaeger"
    assert cfg.jaeger.port == 14268
    assert cfg.jaeger.endpoint == "http://jaeger:14268/api/traces"
    assert cfg.jaeger.service_name == "{{cookiecutter.project_slug}}"


def test_service_defaults():
    cfg = AppSettings()
    svc = cfg.service
    assert svc.name == "{{cookiecutter.project_slug}}"
    assert svc.version == "{{cookiecutter.project_version}}"
    assert svc.host == "0.0.0.0"
    assert svc.port == {{cookiecutter.internal_app_port}}


def test_performance_defaults():
    cfg = AppSettings()
    perf = cfg.performance
    assert perf.uvloop_enabled is True
    assert perf.worker_processes == "auto"
    assert perf.max_concurrent_tasks == 1000
    assert perf.task_timeout == 30
    assert perf.max_payload_size == 1_048_576
    assert perf.shutdown_timeout == 30

