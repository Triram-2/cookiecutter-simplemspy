"""Application configuration models and settings loader."""

import os
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
# The path used for runtime data files.  The default is `<project>/data`,
# but it can be overridden with the ``DATA_DIR`` environment variable.
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    # Fall back to a directory that is always writable inside the container
    fallback = Path(tempfile.gettempdir()) / "{{cookiecutter.project_slug}}_data"
    fallback.mkdir(parents=True, exist_ok=True)
    DATA_DIR = fallback

# Determine where logs should be stored. Default to ``DATA_DIR / 'logs'`` so
# that log files reside next to other runtime data. If the directory is not
# writable, fall back to a temporary folder that is guaranteed to be available.
LOG_DIR: Path = Path(os.getenv("LOG_DIR", str(DATA_DIR / "logs")))
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    fallback_logs = Path(tempfile.gettempdir()) / "{{cookiecutter.project_slug}}_logs"
    fallback_logs.mkdir(parents=True, exist_ok=True)
    LOG_DIR = fallback_logs


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_")

    # Use the pre-created ``LOG_DIR`` as the default log directory.
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
    enqueue: bool = True
    backtrace: bool = True
    diagnose: bool = True
    rotation: str = "00:00"
    retention: str = "7 days"
    # Endpoint where logs should be pushed for aggregation
    # When running inside Docker Compose use the service name
    # rather than localhost so containers can reach Loki
    loki_endpoint: str = "http://loki:3100/loki/api/v1/push"


class RedisSettings(BaseSettings):
    """Configuration for Redis connection and streams."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    # Default to the Docker Compose service hostname
    url: str = "redis://redis:6379/0"
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

    # StatsD exporter hostname within Docker
    host: str = "statsd"
    port: int = 8125
    prefix: str = "microservice"


class JaegerSettings(BaseSettings):
    """Configuration for Jaeger tracing exporter."""

    model_config = SettingsConfigDict(env_prefix="JAEGER_")

    # Jaeger all-in-one hostname within Docker
    host: str = "jaeger"
    port: int = 14268

    endpoint: str = "http://jaeger:14268/api/traces"
    # Name of the service as shown in Jaeger
    service_name: str = "{{cookiecutter.project_slug}}"


class ServiceSettings(BaseSettings):
    """General service information and network settings."""

    model_config = SettingsConfigDict(env_prefix="SERVICE_")

    # Service identifier used in logs and traces
    name: str = "{{cookiecutter.project_slug}}"
    # Application version reported on startup
    version: str = "{{cookiecutter.project_version}}"
    host: str = "0.0.0.0"
    # Internal port the app listens on
    port: int = {{cookiecutter.internal_app_port}}
    # Path for task creation endpoint
    tasks_endpoint: str = "{{cookiecutter.tasks_endpoint_path}}"


class PerformanceSettings(BaseSettings):
    """Runtime performance and tuning parameters."""

    # Enable high performance event loop
    uvloop_enabled: bool = True
    # Number of Uvicorn worker processes
    worker_processes: str = "auto"
    # Limit for concurrent background tasks
    max_concurrent_tasks: int = 1000
    # Individual task timeout in seconds
    task_timeout: int = 30
    # Maximum allowed request payload size in bytes
    max_payload_size: int = 1_048_576
    # Graceful shutdown timeout in seconds
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

    app_host: str = Field(
        default="0.0.0.0", description="Host for Uvicorn"
    )  # Changed default to 0.0.0.0
    app_port: int = Field(default=8000, description="Порт Starlette приложения")
    app_reload: bool = Field(
        default=True, description="Enable/disable Uvicorn auto-reloading"
    )

    app_env: Literal["prod", "dev", "test"] = Field(
        default="prod", description="Application environment: prod, dev, test"
    )


settings: AppSettings = AppSettings()
