import os
from pathlib import Path
from typing import Optional, Union, Any

from pydantic import Field, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# Определяем базовый путь проекта (родительская директория для 'src')
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" # Общая папка для данных

# Вспомогательная функция для LogSettings.path
def _get_log_path_and_create_dir() -> Path:
    log_path = BASE_DIR / "logs"
    os.makedirs(log_path, exist_ok=True)
    return log_path

class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='LOG_')
    path: Path = Field(default_factory=_get_log_path_and_create_dir)
    console_format: str = (
        "<blue>{time:YYYY-MM-DD HH:mm:ss.SSS}</blue> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name: <18}</cyan>| "  # Changed extra[name] to name
        "<cyan>{function}:{line}</cyan> - <level>{message}</level>"
    )
    file_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
        "{name: <18} | " # Changed extra[name] to name
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
    model_config = SettingsConfigDict(env_prefix='DB_')

    type: str = Field(default="SQLITE", description="Тип базы данных: SQLITE или POSTGRESQL")
    
    host: str = "localhost"
    port: int = 5432
    user: Optional[str] = "postgres"
    password: Optional[str] = "postgres"
    name: Optional[str] = "mydatabase"
    
    sqlite_file: Path = Field(default_factory=lambda: DATA_DIR / "db" / "main.sqlite")
    # Прямое задание DATABASE_URL (переопределяет сборку). Полезно для тестов (напр., "sqlite+aiosqlite:///:memory:").
    database_url_override: Optional[str] = Field(default=None, alias="DATABASE_URL") 

    assembled_database_url: Optional[Union[PostgresDsn, str]] = None

    @field_validator("assembled_database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if values := info.data: 
            if forced_url := values.get("database_url_override"):
                if forced_url == "sqlite+aiosqlite:///:memory:" or forced_url == "sqlite:///:memory:":
                    return "sqlite+aiosqlite:///:memory:"
                return forced_url
        
        values = info.data 
        db_type = values.get("type", "SQLITE").upper()

        if db_type == "POSTGRESQL":
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("user"),
                password=values.get("password"),
                host=values.get("host"),
                port=values.get("port"),
                path=f"{values.get('name') or ''}",
            )
        elif db_type == "SQLITE":
            sqlite_path = values.get("sqlite_file")
            if not sqlite_path: 
                sqlite_path = DATA_DIR / "db" / "main.sqlite"
            
            os.makedirs(sqlite_path.parent, exist_ok=True)
            return f"sqlite+aiosqlite:///{sqlite_path.resolve()}"
        
        raise ValueError(f"Неподдерживаемый тип базы данных: {db_type}")

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix='APP_')

    base_dir: Path = BASE_DIR
    data_dir: Path = Field(default_factory=lambda: DATA_DIR)
    
    log: LogSettings = Field(default_factory=LogSettings)
    db: DBSettings = Field(default_factory=DBSettings)

    app_host: str = Field(default="0.0.0.0", description="Хост для запуска Uvicorn")
    app_port: int = Field(default=8000, description="Порт для запуска Uvicorn")
    app_reload: bool = Field(default=True, description="Включить/выключить автоперезагрузку Uvicorn")

    # Окружение приложения (напр., "prod", "dev", "test"). Устанавливается через APP_ENV.
    app_env: str = Field(default="prod", description="Окружение приложения: prod, dev, test")


settings = AppSettings()
