import os
from pathlib import Path
from typing import Optional, Union, Any, Dict, List, Type, Literal

from pydantic import Field, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# Определяем базовый путь проекта (родительская директория для 'src')
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = BASE_DIR / "data"  # Общая папка для данных


# Вспомогательная функция для LogSettings.path
def _get_log_path_and_create_dir() -> Path:
    log_path: Path = BASE_DIR / "logs"
    os.makedirs(log_path, exist_ok=True)
    return log_path


class LogSettings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(env_prefix="LOG_")
    
    path: Path = Field(default_factory=_get_log_path_and_create_dir)
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
    console_level: str = "INFO" # Consider Literal[...] if levels are fixed
    info_file_level: str = "INFO" # Consider Literal[...]
    error_file_level: str = "ERROR" # Consider Literal[...]
    compression: Optional[str] = None
    enqueue: bool = True
    backtrace: bool = True
    diagnose: bool = True
    rotation: str = "00:00"
    retention: str = "7 days"


class DBSettings(BaseSettings): # Renamed from DatabaseSettings in task to match file
    model_config: SettingsConfigDict = SettingsConfigDict(env_prefix="DB_")

    type: Literal["SQLITE", "POSTGRESQL"] = Field( # Using Literal as per description
        default="SQLITE", description="Тип базы данных: SQLITE или POSTGRESQL"
    )

    host: str = "localhost"
    port: int = 5432
    user: Optional[str] = "postgres"
    password: Optional[str] = "postgres"
    name: Optional[str] = "mydatabase" # Corresponds to db_name in task

    # sqlite_file in task is Optional[str], but Path is used here and is more appropriate.
    sqlite_file: Path = Field(default_factory=lambda: DATA_DIR / "db" / "main.sqlite")
    
    # database_url_override in task is Optional[PostgresDsn | str].
    # Here it's Optional[str], which is fine as PostgresDsn will be applied by Pydantic if it matches.
    database_url_override: Optional[str] = Field(default=None, alias="DATABASE_URL")

    # assembled_database_url in task is Optional[PostgresDsn | str].
    assembled_database_url: Optional[Union[PostgresDsn, str]] = None

    @field_validator("assembled_database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Union[PostgresDsn, str]:
        # `v` is the current value of `assembled_database_url` (None if not set)
        # `info.data` contains the raw data provided to the model
        values: Dict[str, Any] = info.data # Existing data in the model
        
        forced_url: Optional[Any] = values.get("database_url_override")
        if forced_url:
            # Special handling for in-memory SQLite for tests
            if forced_url in ["sqlite+aiosqlite:///:memory:", "sqlite:///:memory:"]:
                return "sqlite+aiosqlite:///:memory:"
            # If forced_url is a valid PostgresDsn string, Pydantic will handle it.
            # If it's any other string, it will be returned as is.
            return str(forced_url) # Ensure it's a string if not None

        # If database_url_override is not set, assemble from other fields
        db_type: str = values.get("type", "SQLITE").upper()

        if db_type == "POSTGRESQL":
            # Ensure all components for PostgresDsn are present or have defaults
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
                path=f"/{pg_name}" if pg_name else None, # Path should start with /
            )
        elif db_type == "SQLITE":
            sqlite_path_val: Optional[Any] = values.get("sqlite_file")
            sqlite_path: Path
            if isinstance(sqlite_path_val, Path):
                sqlite_path = sqlite_path_val
            else: # Fallback if not a Path (e.g. if loaded as string)
                sqlite_path = DATA_DIR / "db" / "main.sqlite"

            # Ensure the directory for the SQLite file exists
            os.makedirs(sqlite_path.parent, exist_ok=True)
            return f"sqlite+aiosqlite:///{sqlite_path.resolve()}"

        raise ValueError(f"Неподдерживаемый тип базы данных: {db_type}")


class AppSettings(BaseSettings): # Renamed from Settings in task to match file
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="ignore", env_prefix="APP_"
    )

    # Fields from task description to be typed if they align with existing ones or can be added
    # app_name: str = "MyApplication" # Example, not in original file
    # debug: bool = False # Example, not in original file
    # app_version: str = "0.1.0" # Example, not in original file
    
    base_dir: Path = BASE_DIR # Corresponds to project_dir in task description
    data_dir: Path = Field(default_factory=lambda: DATA_DIR) # Matches data_dir in task

    log: LogSettings = Field(default_factory=LogSettings)
    db: DBSettings = Field(default_factory=DBSettings) # Renamed from DatabaseSettings

    app_host: str = Field(default="0.0.0.0", description="Хост для запуска Uvicorn")
    app_port: int = Field(default=8000, description="Порт для запуска Uvicorn")
    app_reload: bool = Field(
        default=True, description="Включить/выключить автоперезагрузку Uvicorn"
    )

    # app_env in file, environment in task. Using Literal as suggested.
    app_env: Literal["prod", "dev", "test"] = Field(
        default="prod", description="Окружение приложения: prod, dev, test"
    )
    
    # sentry_dsn: Optional[str] = None # Example, not in original file
    # api_v1_prefix: str = "/api/v1" # Example, not in original file
    # openapi_url: Optional[str] = "/openapi.json" # Example, not in original file
    # docs_url: Optional[str] = "/docs" # Example, not in original file
    # redoc_url: Optional[str] = "/redoc" # Example, not in original file


settings: AppSettings = AppSettings()
