import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Определяем базовый путь проекта (родительская директория для 'src')
# Это позволит гибко строить пути к другим директориям
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class LogSettings(BaseSettings):
    # Модель для настроек логирования
    # Префикс для переменных окружения LOG_...
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

class AppSettings(BaseSettings):
    # Основная модель настроек приложения
    # Можно добавить сюда другие настройки, например, для базы данных, кэша и т.д.
    # Префикс для переменных окружения APP_... (если понадобится)
    # model_config = SettingsConfigDict(env_prefix='APP_')

    base_dir: Path = BASE_DIR
    log: LogSettings = Field(default_factory=LogSettings)

    # Пример для других путей, если они понадобятся в будущем
    # data_dir: Path = Field(default_factory=lambda: BASE_DIR / "data")
    # cache_dir: Path = Field(default_factory=lambda: data_dir.default_factory() / "cache") # type: ignore

# Создаем экземпляр настроек для использования в приложении
settings = AppSettings()

# Пример того, как можно будет обращаться к настройкам:
# from src.core.config import settings
# print(settings.log.path)
# print(settings.log.console_level)
