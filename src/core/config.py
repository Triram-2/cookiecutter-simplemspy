import os
from pathlib import Path
from typing import Optional, Union

from pydantic import Field, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# Определяем базовый путь проекта (родительская директория для 'src')
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" # Общая папка для данных

class LogSettings(BaseSettings):
    # Модель для настроек логирования
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
    compression: Optional[str] = None # Например, "zip"
    enqueue: bool = True
    backtrace: bool = True
    diagnose: bool = True
    rotation: str = "00:00"  # Ежедневная ротация в полночь
    retention: str = "7 days" # Хранить логи за 7 дней

class DBSettings(BaseSettings):
    # Модель для настроек базы данных
    model_config = SettingsConfigDict(env_prefix='DB_')

    type: str = Field(default="SQLITE", description="Тип базы данных: SQLITE или POSTGRESQL")
    
    # Настройки PostgreSQL
    host: str = "localhost"
    port: int = 5432
    user: Optional[str] = "postgres"
    password: Optional[str] = "postgres"
    name: Optional[str] = "mydatabase" # Имя базы данных
    
    # Настройки SQLite
    # Путь к файлу SQLite относительно DATA_DIR
    sqlite_file: Path = Field(default_factory=lambda: DATA_DIR / "db" / "main.sqlite") 

    # SQLAlchemy DATABASE_URL будет собран здесь
    database_url: Optional[Union[PostgresDsn, str]] = None

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> any:
        # Валидатор для автоматической сборки URL подключения к БД
        if isinstance(v, str): # Если URL уже задан напрямую, используем его
            return v
        
        values = info.data # Получаем уже загруженные значения (type, host, etc.)
        db_type = values.get("type", "SQLITE").upper() # Тип БД, по умолчанию SQLITE

        if db_type == "POSTGRESQL":
            # Убедимся, что директория для данных существует (хотя PG не пишет сюда напрямую)
            # Это больше для консистентности структуры папок
            os.makedirs(DATA_DIR / "db", exist_ok=True) 
            return PostgresDsn.build(
                scheme="postgresql+asyncpg", # Используем асинхронный драйвер asyncpg
                username=values.get("user"),
                password=values.get("password"),
                host=values.get("host"),
                port=values.get("port"),
                path=f"{values.get('name') or ''}", # Имя БД
            )
        elif db_type == "SQLITE":
            sqlite_path = values.get("sqlite_file")
            if not sqlite_path: # Если по какой-то причине default_factory не сработал
                sqlite_path = DATA_DIR / "db" / "main.sqlite"
            
            # Убедимся, что директория для SQLite файла существует
            os.makedirs(sqlite_path.parent, exist_ok=True)
            # Используем resolve() для получения абсолютного пути к файлу SQLite
            return f"sqlite+aiosqlite:///{sqlite_path.resolve()}" # Асинхронный драйвер aiosqlite
        
        raise ValueError(f"Неподдерживаемый тип базы данных: {db_type}")

class AppSettings(BaseSettings):
    # Основная модель настроек приложения
    base_dir: Path = BASE_DIR
    data_dir: Path = Field(default_factory=lambda: DATA_DIR) # Добавляем data_dir
    
    log: LogSettings = Field(default_factory=LogSettings) # Настройки логирования
    db: DBSettings = Field(default_factory=DBSettings)   # Настройки базы данных

    # Если вы планируете использовать .env файл для переопределения настроек:
    # model_config = SettingsConfigDict(env_file=".env", extra="ignore") 

# Создаем глобальный экземпляр настроек для использования в приложении
settings = AppSettings()

# Примеры использования (можно удалить или закомментировать):
# print(f"Тип БД: {settings.db.type}")
# print(f"URL БД: {settings.db.database_url}")
# print(f"Путь к логам: {settings.log.path}")
# print(f"Директория данных: {settings.data_dir}")
# if settings.db.type == "SQLITE":
#     print(f"Путь к файлу SQLite: {settings.db.sqlite_file.resolve()}")
#
# # Проверка создания директорий (если их еще нет)
# if not settings.log.path.exists():
#      print(f"Директория логов {settings.log.path} будет создана.")
# if settings.db.type == "SQLITE" and not settings.db.sqlite_file.parent.exists():
#      print(f"Директория для SQLite {settings.db.sqlite_file.parent} будет создана.")
