"""Application configuration models and settings loader."""

import os
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent


def _init_data_dir() -> Path:
    """Return a writable directory for runtime data."""
    data_dir = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        fallback = Path(tempfile.gettempdir()) / "{{cookiecutter.project_slug}}_data"
        fallback.mkdir(parents=True, exist_ok=True)
        data_dir = fallback
    return data_dir


DATA_DIR: Path = _init_data_dir()


def _init_log_dir(data_dir: Path) -> Path:
    """Return a writable directory for log files."""
    log_dir = Path(os.getenv("LOG_DIR", str(data_dir / "logs")))
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        fallback_logs = (
            Path(tempfile.gettempdir()) / "{{cookiecutter.project_slug}}_logs"
        )
        fallback_logs.mkdir(parents=True, exist_ok=True)
        log_dir = fallback_logs
    return log_dir


LOG_DIR: Path = _init_log_dir(DATA_DIR)


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_")

    path: Path = LOG_DIR
    console_format: str = (
        "<blue>{time:YYYY-MM-DD HH:mm:ss.SSS}</blue> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name: <18}</cyan>| "
        "<cyan>{function}:{line}</cyan> - <level>{message}</level>"
    )
    file_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
        "{name: <18} | "
        "{name}:{function}:{line} - {message}"
    )
    console_level: str = "INFO"
    info_file_level: str = "INFO"
    error_file_level: str = "ERROR"
    compression: str | None = None
    enqueue: bool = False
    backtrace: bool = True
    diagnose: bool = True
    rotation: str = "00:00"
    retention: str = "7 days"
    loki_endpoint: str = "http://loki:3100/loki/api/v1/push"


def _default_redis_url() -> str:
    """Return a Redis URL appropriate for the environment."""
    in_container = Path("/.dockerenv").exists()
    return "redis://redis:6379/0" if in_container else "redis://127.0.0.1:6379/0"


class RedisSettings(BaseSettings):
    """Configuration for Redis connection and streams."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    url: str = Field(default_factory=_default_redis_url)
    stream_name: str = "{{cookiecutter.redis_stream_name}}"
    consumer_group: str = "{{cookiecutter.redis_consumer_group}}"
    consumer_name: str = "{{cookiecutter.redis_consumer_name}}"
    max_length: int = 100_000
    retention_ms: int = 3_600_000
    breaker_fail_max: int = 3
    breaker_reset_timeout: int = 30


class StatsDSettings(BaseSettings):
    """Configuration for StatsD metrics."""

    model_config = SettingsConfigDict(env_prefix="STATSD_")

    host: str = "statsd"
    port: int = 9125
    prefix: str = "{{cookiecutter.project_slug}}"


class JaegerSettings(BaseSettings):
    """Configuration for Jaeger tracing exporter."""

    model_config = SettingsConfigDict(env_prefix="JAEGER_")

    host: str = "jaeger"
    port: int = 14268

    endpoint: str = "http://jaeger:14268/api/traces"
    service_name: str = "{{cookiecutter.project_slug}}"


class ServiceSettings(BaseSettings):
    """General service information and network settings."""

    model_config = SettingsConfigDict(env_prefix="SERVICE_")

    name: str = "{{cookiecutter.project_slug}}"
    version: str = "{{cookiecutter.project_version}}"
    host: str = "0.0.0.0"
    port: int = {{cookiecutter.internal_app_port}}
    tasks_endpoint: str = "{{cookiecutter.tasks_endpoint_path}}"


class PerformanceSettings(BaseSettings):
    """Runtime performance and tuning parameters."""

    uvloop_enabled: bool = True
    worker_processes: str = "auto"
    max_concurrent_tasks: int = 1000
    task_timeout: int = 30
    max_payload_size: int = 1_048_576
    shutdown_timeout: int = 30


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_prefix="APP_"
    )

    base_dir: Path = BASE_DIR
    data_dir: Path = Field(default_factory=lambda: DATA_DIR)

    log: LogSettings = Field(default_factory=LogSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    statsd: StatsDSettings = Field(default_factory=StatsDSettings)
    jaeger: JaegerSettings = Field(default_factory=JaegerSettings)
    service: ServiceSettings = Field(default_factory=ServiceSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)

    app_host: str = Field(default="0.0.0.0", description="Host for Uvicorn")
    app_port: int = Field(
        default={{cookiecutter.app_port_host}}, description="Порт Starlette приложения"
    )
    app_reload: bool = Field(
        default=True, description="Enable/disable Uvicorn auto-reloading"
    )

    app_env: Literal["prod", "dev", "test"] = Field(
        default="prod", description="Application environment: prod, dev, test"
    )


settings: AppSettings = AppSettings()
