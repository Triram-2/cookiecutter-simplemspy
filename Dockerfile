# Dockerfile

# --- Стадия сборки зависимостей ---
FROM python:3.12-slim AS builder

LABEL stage="builder"

# Устанавливаем переменные окружения для pip и uv
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    UV_SYSTEM_PYTHON=true \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем uv
RUN pip install uv

# Устанавливаем рабочую директорию
WORKDIR /app

# Создаем виртуальное окружение
# Используем python из базового образа, чтобы uv его нашел
RUN uv venv /opt/venv --python $(which python)

# Копируем файлы проекта, необходимые для установки зависимостей
COPY pyproject.toml uv.lock* ./ 
# uv.lock* для случая, если lock файл называется uv.lock или имеет суффикс платформы

# Устанавливаем зависимости в виртуальное окружение
# Используем --no-deps, если все зависимости точно указаны в lock файле или toml
# Если есть зависимости только для разработки, которые не нужны в финальном образе,
# то лучше использовать `uv pip install --no-dev ...` или `uv sync --no-dev`.
# Для простоты шаблона, пока установим все (кроме dev, если `uv sync` их не ставит по умолчанию).
# Если uv.lock существует, uv sync его использует. Иначе, он может попытаться разрешить зависимости из pyproject.toml.
# Предполагаем, что uv.lock будет сгенерирован и будет основным источником.
RUN . /opt/venv/bin/activate && uv sync --no-dev --frozen-lockfile || \
    ( . /opt/venv/bin/activate && uv pip install --no-cache --no-dev . )
# Добавил --no-dev для уменьшения образа, если это поддерживается uv sync или pip install для проекта.
# Добавил --frozen-lockfile для uv sync, чтобы он падал, если lock не соответствует toml.

# --- Финальная стадия ---
FROM python:3.12-slim AS runner

LABEL stage="runner"

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    # Путь к файлу БД SQLite внутри контейнера (если используется)
    # Может быть переопределен через DB_SQLITE_FILE в .env
    APP_SQLITE_DB_PATH="/app/data/db/main.sqlite" 

# Создаем группу и пользователя приложения
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin -c "Application User" appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем виртуальное окружение со стадии сборки
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv

# Копируем исходный код приложения
# Убедимся, что .dockerignore настроен правильно, чтобы не копировать лишнее
COPY --chown=appuser:appgroup ./src ./src

# Создаем директорию для данных, если SQLite будет использоваться внутри контейнера
# и устанавливаем права (пример)
RUN mkdir -p /app/data/db && chown -R appuser:appgroup /app/data

# Устанавливаем пользователя приложения
USER appuser

# Открываем порт, на котором будет работать приложение
# Этот порт должен соответствовать порту в CMD Uvicorn
EXPOSE 8000 
# (Примечание: CMD ниже использует порт 8000, если APP_PORT не задан. Согласуем с APP_PORT из AppSettings)
# Если Uvicorn в CMD будет запускаться на порту 80, то EXPOSE 80

# Команда для запуска приложения
# Используем переменные окружения для хоста и порта, если они заданы,
# иначе значения по умолчанию из AppSettings (которые мы передадим через .env или docker-compose)
# или значения по умолчанию для Uvicorn.
# Для простоты, здесь можно захардкодить порт, на котором Uvicorn слушает внутри контейнера,
# а маппинг на хостовой порт делать в docker-compose.yml.
# Пусть Uvicorn внутри контейнера всегда слушает на 8000.
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
