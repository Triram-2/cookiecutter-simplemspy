import os
from pathlib import Path
from typing import Optional, Union, Any, Dict, Literal

from pydantic import Field, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # Ensure DATA_DIR exists
(DATA_DIR / "db").mkdir(parents=True, exist_ok=True)  # Ensure DATA_DIR/db exists


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


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    type: Literal["SQLITE", "POSTGRESQL"] = Field(
        default="SQLITE", description="Database type: SQLITE or POSTGRESQL"
    )

    host: str = "{{cookiecutter.db_host}}"
    port: int = Field(default=5432, description="Порт базы данных")
    user: Optional[str] = "{{cookiecutter.db_user}}"
    password: Optional[str] = "{{cookiecutter.db_password}}"
    name: Optional[str] = "{{cookiecutter.db_name}}"

    sqlite_file: Path = DATA_DIR / "db/main.sqlite" # Changed BASE_DIR to DATA_DIR and path

    database_url_override: Optional[str] = Field(default=None, alias="DATABASE_URL")

    assembled_database_url: Optional[Union[PostgresDsn, str]] = None

    @field_validator("assembled_database_url", mode="before")
    @classmethod
    def assemble_db_connection(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Union[PostgresDsn, str]:
        values: Dict[str, Any] = info.data

        forced_url: Optional[Any] = values.get("database_url_override")
        if forced_url:
            if forced_url in ["sqlite+aiosqlite:///:memory:", "sqlite:///:memory:"]:
                return "sqlite+aiosqlite:///:memory:"
            return str(forced_url)

        db_type: str = values.get("type", "SQLITE").upper()

        if db_type == "POSTGRESQL":
            pg_user: Optional[str] = values.get("user")
            pg_password: Optional[str] = values.get("password")
            pg_host: str = values.get("host", "localhost")
            pg_port: int = values.get("port", 5432)
            pg_name: Optional[str] = values.get("name")

            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=pg_user,
                password=pg_password,
                host=pg_host,
                port=pg_port,
                path=f"/{pg_name}" if pg_name else None,
            )
        elif db_type == "SQLITE":
            sqlite_path_val: Optional[Any] = values.get("sqlite_file")
            sqlite_path: Path
            if isinstance(sqlite_path_val, Path):
                sqlite_path = sqlite_path_val
            else:
                # Ensure the directory for the SQLite file exists
                sqlite_path = DATA_DIR / "db/main.sqlite" # Changed BASE_DIR to DATA_DIR and path
                os.makedirs(sqlite_path.parent, exist_ok=True)

            return f"sqlite+aiosqlite:///{sqlite_path.resolve()}"

        raise ValueError(f"Unsupported database type: {db_type}")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_prefix="APP_"
    )

    base_dir: Path = BASE_DIR
    data_dir: Path = Field(default_factory=lambda: DATA_DIR)

    log: LogSettings = Field(default_factory=LogSettings)
    db: DBSettings = Field(default_factory=DBSettings)

    app_host: str = Field(default="0.0.0.0", description="Host for Uvicorn") # Changed default to 0.0.0.0
    app_port: int = Field(default=8000, description="Порт FastAPI приложения")
    app_reload: bool = Field(
        default=True, description="Enable/disable Uvicorn auto-reloading"
    )

    app_env: Literal["prod", "dev", "test"] = Field(
        default="prod", description="Application environment: prod, dev, test"
    )


settings: AppSettings = AppSettings()
