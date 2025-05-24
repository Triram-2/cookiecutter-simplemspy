"""
Основная точка входа для запуска FastAPI приложения с использованием Uvicorn.

Этот файл можно использовать для запуска приложения напрямую:
  `python src/main.py`

Или передать его Uvicorn для запуска:
  `uvicorn src.main:app --reload` (где `app` - это экземпляр FastAPI из `src.api`)
  Обратите внимание, что при запуске через `uvicorn src.main:app`, uvicorn будет искать
  объект `app` в этом файле. Если вы хотите, чтобы uvicorn запускал приложение
  из `src.api.main:app` (или `src.api:app`), то команда будет `uvicorn src.api:app --reload`.
  Данный `main.py` предоставляет удобный способ запуска с уже примененными настройками
  из `src.core.config.settings`.
"""

# Добавим стандартный лог для проверки InterceptHandler
import logging

import uvicorn

# Импортируем сам объект FastAPI приложения.
# Он экспортируется из src.api.__init__, который в свою очередь импортирует его из src.api.main
from src.core.config import settings
from src.core.logging_config import get_logger  # Импортируем наш логгер

# Получаем экземпляр логгера для этого модуля
# (хотя базовая конфигурация логгера уже должна была произойти при импорте logging_config)
log = get_logger(__name__)


std_logger = logging.getLogger("test_std_logging")
std_logger.setLevel(
    logging.INFO
)  # Убедимся, что уровень позволяет этому сообщению пройти

if __name__ == "__main__":
    std_logger.info(
        "Это тестовое сообщение от стандартного logging."
    )  # Это сообщение должно быть перехвачено
    log.info(  # type: ignore[misc]
        f"Запуск Uvicorn сервера на http://{settings.app_host}:{settings.app_port}"
    )
    log.info(  # type: ignore[misc]
        f"Автоперезагрузка при изменениях кода: {'Включена' if settings.app_reload else 'Выключена'}"
    )
    log.info("Для остановки сервера нажмите CTRL+C")  # type: ignore[misc]

    uvicorn.run(
        # Путь к объекту FastAPI приложения.
        # "src.api:app" означает, что Uvicorn будет искать объект `app`
        # в модуле `src.api` (который является `src/api/__init__.py`).
        # В `src/api/__init__.py` мы экспортируем `app` из `src.api.main`.
        "src.api:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
        # Можно добавить другие параметры Uvicorn по необходимости, например:
        # log_level=settings.log.console_level.lower(), # Если хотим синхронизировать уровень логов
        # workers=settings.app_workers, # Если добавим app_workers в AppSettings
    )

# Если вы хотите иметь возможность импортировать `app` из `src.main`
# (например, для `uvicorn src.main:app`), то `app` должен быть доступен здесь.
# Он уже импортирован выше: `from src.api import app`
