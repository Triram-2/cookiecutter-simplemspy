import sys
import os
import logging
import uvicorn

# Path manipulation and module aliasing code
# This block needs to be before any project-specific imports that rely on these paths.
_src_path = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_src_path)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Ensure 'src' is imported. Add noqa for E402 if Ruff flags it due to path code above.
import src  # noqa: E402

# Alias 'name' to 'src' module. This must be after 'import src' and after path setup.
sys.modules["name"] = src

# Imports from the 'name' (src) package. Add noqa for E402 if Ruff flags them.
from name.core.config import settings  # noqa: E402
from name.core.logging_config import get_logger  # noqa: E402

"""
Основная точка входа для запуска FastAPI приложения с использованием Uvicorn.

Этот файл можно использовать для запуска приложения напрямую:
  `python src/main.py`

Или передать его Uvicorn для запуска:
  `uvicorn name.main:app --reload` (где `app` - это экземпляр FastAPI из `name.api`)
  Обратите внимание, что при запуске через `uvicorn name.main:app`, uvicorn будет искать
  объект `app` в этом файле. Если вы хотите, чтобы uvicorn запускал приложение
  из `name.api.main:app` (или `name.api:app`), то команда будет `uvicorn name.api:app --reload`.
  Данный `main.py` предоставляет удобный способ запуска с уже примененными настройками
  из `name.core.config.settings`.
"""

# Добавим стандартный лог для проверки InterceptHandler

# Импортируем сам объект FastAPI приложения.
# Он экспортируется из name.api.__init__, который в свою очередь импортирует его из name.api.main

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
        # "name.api:app" означает, что Uvicorn будет искать объект `app`
        # в модуле `name.api` (который является `src/api/__init__.py`).
        # В `src/api/__init__.py` мы экспортируем `app` из `src.api.main`.
        "name.api:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
        # Можно добавить другие параметры Uvicorn по необходимости, например:
        # log_level=settings.log.console_level.lower(), # Если хотим синхронизировать уровень логов
        # workers=settings.app_workers, # Если добавим app_workers в AppSettings
    )

# Если вы хотите иметь возможность импортировать `app` из `name.main`
# (например, для `uvicorn name.main:app`), то `app` должен быть доступен здесь.
# Он уже импортирован выше: `from name.api import app`
