import os
from pathlib import Path
from typing import Optional, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # Ensure DATA_DIR exists


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_")

    _ = os.makedirs(BASE_DIR / "logs", exist_ok=True)
    path: Path = BASE_DIR / "logs"
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
    compression: Optional[str] = None
    enqueue: bool = True
    backtrace: bool = True
    diagnose: bool = True
    rotation: str = "00:00"
    retention: str = "7 days"
    loki_url: str = "http://localhost:3100/loki/api/v1/push"


class RedisSettings(BaseSettings):
    """Configuration for Redis connection and streams."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    url: str = "redis://localhost:6379/0"
    stream_name: str = "tasks:stream"
    consumer_group: str = "processors"
    consumer_name: str = f"{os.getenv('HOSTNAME', 'local')}:{os.getpid()}"
    max_length: int = 100_000
    retention_ms: int = 3_600_000
    breaker_fail_max: int = 3
    breaker_reset_timeout: int = 30


class StatsDSettings(BaseSettings):
    """Configuration for StatsD metrics."""

    model_config = SettingsConfigDict(env_prefix="STATSD_")

    host: str = "localhost"
    port: int = 8125


class JaegerSettings(BaseSettings):
    """Configuration for Jaeger tracing exporter."""

    model_config = SettingsConfigDict(env_prefix="JAEGER_")

    host: str = "localhost"
    port: int = 14268


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

    app_host: str = Field(
        default="0.0.0.0", description="Host for Uvicorn"
    )  # Changed default to 0.0.0.0
    app_port: int = Field(default=8000, description="Порт FastAPI приложения")
    app_reload: bool = Field(
        default=True, description="Enable/disable Uvicorn auto-reloading"
    )

    app_env: Literal["prod", "dev", "test"] = Field(
        default="prod", description="Application environment: prod, dev, test"
    )


settings: AppSettings = AppSettings()
