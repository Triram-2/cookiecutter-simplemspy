import os
from pathlib import Path
from typing import Optional, Union, Any

from pydantic import Field, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# Определяем базовый путь проекта (родительская директория для 'src')
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" # Общая папка для данных

class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='LOG_')
    path: Path = Field(default_factory=lambda: BASE_DIR / "logs")
    console_format: str = (
        "<blue>{time:YYYY-MM-DD HH:mm:ss.SSS}</blue> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[name]: <18}</cyan>| "
        "<cyan>{function}:{line}</cyan> - <level>{message}</level>"
    )
    file_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
        "{extra[name]: <18} | "
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
    # Позволяет напрямую установить DATABASE_URL, переопределяя сборку
    # Это полезно для тестов, где мы можем захотеть использовать in-memory SQLite
    # или специфичный тестовый URL.
    # Пример: DB_DATABASE_URL="sqlite+aiosqlite:///:memory:"
    database_url_override: Optional[str] = Field(default=None, alias="DATABASE_URL") 

    assembled_database_url: Optional[Union[PostgresDsn, str]] = None

    @field_validator("assembled_database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        # Если database_url_override (DB_DATABASE_URL) задан, используем его
        if values := info.data: # Проверяем, что values не пустой
            if forced_url := values.get("database_url_override"):
                # Если это :memory: SQLite, нужно обеспечить правильный формат
                if forced_url == "sqlite+aiosqlite:///:memory:" or forced_url == "sqlite:///:memory:":
                     # Убедимся, что директория для логов существует, даже для in-memory
                    os.makedirs(BASE_DIR / "logs", exist_ok=True)
                    # Для in-memory SQLite не нужно создавать папки для файла БД
                    return "sqlite+aiosqlite:///:memory:"
                return forced_url
        
        # Иначе, собираем URL как раньше, на основе DB_TYPE
        # (Этот блок остается идентичным предыдущей версии)
        values = info.data # Получаем уже загруженные значения (type, host, etc.)
        db_type = values.get("type", "SQLITE").upper()

        if db_type == "POSTGRESQL":
            # Убедимся, что директория для логов существует
            os.makedirs(BASE_DIR / "logs", exist_ok=True) 
            # Для PostgreSQL не нужно создавать папки для файла БД здесь
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
            # Убедимся, что директория для логов существует
            os.makedirs(BASE_DIR / "logs", exist_ok=True)
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

    # Новое поле для определения окружения (полезно для тестов)
    # Может быть установлено через переменную окружения APP_ENV=test
    app_env: str = Field(default="prod", description="Окружение приложения: prod, dev, test")


settings = AppSettings()

# Для удобства доступа к актуальному URL базы данных
# Теперь нужно использовать settings.db.assembled_database_url
# Старый settings.db.database_url был переименован в settings.db.database_url_override
# и используется для прямого задания URL.

# Пример вывода для проверки (можно удалить)
# print(f"DB Type: {settings.db.type}")
# print(f"DB URL Override: {settings.db.database_url_override}")
# print(f"Assembled DB URL: {settings.db.assembled_database_url}")
# print(f"App Env: {settings.app_env}")
