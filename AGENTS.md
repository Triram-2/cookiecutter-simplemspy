## 0. INSTRUCTIONS FOR CODEX
* Run `nox -s ci-3.12 ci-3.13` before committing  
* Touch only files inside `src/` and corresponding tests  
* Never edit generated folders (`additional/`, `docs/_build`)  
* Use `pytest -q` to run quick subset of tests first

## 1. ОБЩАЯ ЧАСТЬ (Системные стандарты)
### 1.1 Структура и организация проекта

* Standard Python src‑layout
* `src/` – application code
* `data/` - all data
* `logs/` - all logs
* `tests/` – unit & integration tests
* `docs/` – documentation
* `scripts/` – automation
* `additional/` – additional utilities
* Entry point: `src/{{cookiecutter.python_package_name}}/main.py`

### 1.2 Стандарты кодирования

* **Python** 3.13
* PEP 8 + ruff formatting, max line 88 chars
* snake\_case for vars & funcs, PascalCase for classes
* Mandatory type hints
* Google‑style docstrings

### 1.3 Паттерны и принципы

* SOLID, DRY, KISS, Clean Code
* Layered architecture: API → Service → Repository → Models
* Dependency Injection for testability
* Explicit error handling
* **Fire-and-forget** messaging pattern
* **202 Accepted** для мгновенного ответа

### 1.4 Тестирование

* Framework: **pytest+pytest-asyncio**
* Minimum coverage: 80 %
* `tests/unit/`, `tests/integration/`
* Naming: `test_should_<expected>_when_<condition>`

### 1.5 Обработка ошибок

* Fail‑fast strategy
* Custom domain exceptions
* Structured logging of errors

### 1.6 Безопасность

* Validate & sanitize all inputs
* Secrets only via env vars
* Parameterized queries, XSS escaping

### 1.7 API & интерфейсы

* **Starlette** + **Uvicorn** for maximum performance
* REST API, JSON
* Without versioning
* Schemas via **Pydantic**
* **Немедленный ответ 202 Accepted** для всех запросов

### 1.8 Логирование и мониторинг

* **Grafana Loki** для логов
* **StatsD** для метрик  
* **Jaeger** для трейсов
* Used src/core/logging_config.py!
* Config logging in src/core/config.py.

### 1.9 Конфигурация

* All settings via src/core/config or `.env`
* Validation with **Pydantic Settings**

### 1.10 Зависимости

* Dependency manager: **uv**
* Pin versions in `uv.lock`
* Regular vuln scanning

### 1.11 Git & версионирование

* GitHub Flow
* Conventional Commits messages (EN, imperative)
* PRs required for main
* ≥1 reviewer

### 1.12 Документация

* Auto API docs (OpenAPI)
* Sphinx for code docs
* Keep `README.md` & `CHANGELOG.md` up‑to‑date

### 1.13 Команды и скрипты

* Full list commands nox: `nox -l`
* Dev: `uv run src/{{cookiecutter.python_package_name}}/main.py`
* Test: `nox -s test-3.12 test-3.13`
* Lint: `nox -s lint-3.12 lint-3.13`
* Full CI: `nox -s ci-3.12 ci-3.13`
* Format: `uv run ruff format`
* Docs: `nox -s docs`
* Scalene: `nox -s profile`
* Build docker-image: `nox -s build`
* Clean non-need files: `nox -s clean`
* Locust: `nox -s locust`

### 1.14 Полный список инструментов при разработке.

* **Docker** 
* **git**
* **Nox**
* **ruff** (lint + format)
* **pyright** (type checking)
* **pytest** (tests)
* **coverage** (measuring test coverage)
* **hypothesis** (property-based testing)
* **locust** (distributed load testing)
* **pip-audit** (dependency vulnerability scanning)
* **Sphinx** (docs)
* **Scalene** (CPU and memory profiling)
* **commitizen** (commit message standardization)

### 1.15 Полный список фреймворков при разработке.
## НЕ разрешается пользоваться иными фреймворками БЕЗ РАЗРЕШЕНИЯ!

# Системные и базовые
* **os**
* **sys**
* **multiprocessing**+**asyncio**+**uvloop**
* **datetime**
* **pathlib**
* **types**
* **typing**
* **enum**

# Веб-фреймворки и API
* **Starlette** (высокопроизводительный ASGI фреймворк)
* **Uvicorn** (ASGI сервер с uvloop)

# Сериализация и валидация
* **Pydantic**+**pydantic_settings**
* **Quickle** (быстрый pickle)
* **msgspec** (быстрая сериализация)
* **orjson** (ультра-быстрый JSON)

# Сеть и HTTP
* **httpx-rust** (ультра-быстрый HTTP клиент)
* **Playwright Stealth** (альтернатива selenium_driverless)
* **Selectolax + Lexbor** (альтернатива bs4+lxml)
* **aioredis** (Redis для asyncio)

# Очереди и брокеры сообщений
* **Redis Streams** (основной брокер)
* **aioredis** (Redis клиент)

# Вычисления
* **FireDucks** (быстрая альтернатива pandas, Polars)
* **Numba** (JIT компилятор)

# Интерфейсы
* **rich** (красивый вывод в терминал)
* **Typer** (CLI)
* **tqdm** (прогресс-бары)

# Логирование
* **Loguru** (структурированные логи)

# Мониторинг и трейсинг
* **OpenTelemetry** (трейсинг → Jaeger)
* **statsd** (метрики → Grafana)
* **python-json-logger** (для Loki)

# Системные утилиты
* **Psutil**
* **aiofile** (асинхронная работа с файлами)

# Валидация и безопасность
* **Pydantic** (валидация данных)

## 2. ТЕХНИЧЕСКОЕ ЗАДАНИЕ Микросервиса-Темплейта `cookiecutter-high-performance-pyms`

### 2.1 Общая информация

* **Название микросервиса-темплейта:** `cookiecutter-high-performance-pyms`
* **Входит в систему:** Экосистема высокопроизводительных микросервисов
* **Описание системы:** Cookiecutter темплейт для создания максимально производительных микросервисов с fire-and-forget архитектурой
* **Зависит от:** Redis Streams, StatsD, Jaeger, Loki
* **Используется:** Разработчиками для создания новых микросервисов

### 2.2 Назначение и цели

#### Основная цель

Создать универсальный cookiecutter темплейт для генерации высокопроизводительных микросервисов с максимальной нагрузоустойчивостью, мгновенным откликом API и асинхронной обработкой задач через Redis Streams.

#### Задачи микросервиса-темплейта

* Обеспечить максимальную производительность API (< 1ms response time)
* Реализовать fire-and-forget архитектуру с Redis Streams
* Обеспечить горизонтальную масштабируемость без ограничений
* Интегрировать полный стек мониторинга (StatsD, Jaeger, Loki)
* Предоставить готовую инфраструктуру для разработки и тестирования

#### Место в архитектуре

Базовый темплейт для создания микросервисов в экосистеме высокопроизводительных распределенных систем. Каждый сгенерированный микросервис будет автономным, stateless и способным обрабатывать максимальную нагрузку.

### 2.3 Функциональные требования

#### 2.3.1 Основная функциональность

Темплейт должен генерировать микросервис с минимальной базовой функциональностью:
- Health check endpoint
- Универсальный POST endpoint для задач
- Интеграция с Redis Streams
- Полный стек мониторинга
- Graceful shutdown

#### 2.3.2 API Endpoints

##### Health Check Endpoint

* **Метод:** GET
* **Путь:** `/health`
* **Описание:** Проверка состояния сервиса и зависимостей
* **Входные параметры:** Отсутствуют

* **Мгновенный ответ (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "redis_connected": true,
  "version": "1.0.0"
}
```

* **Коды ответов:**
  * 200: Сервис работает нормально
  * 503: Сервис недоступен (Redis отключен)

#### 2.3.3 Бизнес‑логика

Темплейт не содержит специфической бизнес-логики. Базовая логика:
- Валидация входных данных через Pydantic
- Отправка задачи в Redis Streams(получение задачи будет дописано в реальных микросервисах, не в темплейте)
- Мгновенный ответ 202 Accepted
- Асинхронная обработка в фоновом режиме

#### 2.3.4 Валидация данных

* Все входные данные валидируются через Pydantic schemas
* Обязательная проверка структуры JSON
* Санитизация всех строковых полей
* Ограничение размера payload (по умолчанию 1MB)

### 2.4 Технические требования

#### 2.4.1 Технологический стек

* **ASGI Framework:** Starlette
* **ASGI Server:** Uvicorn с uvloop
* **Message Broker:** Redis Streams
* **Monitoring:** StatsD + Grafana + Loki + Jaeger
* **Serialization:** orjson + msgspec
* **Validation:** Pydantic

#### 2.4.2 Архитектурные паттерны

* **Fire-and-forget messaging**
* **Immediate response (202 Accepted)**
* **Fully asynchronous processing**
* **Event-driven architecture**
* **Circuit breaker pattern**
* **Bulkhead isolation**

#### 2.4.3 Зависимости

##### Внешние сервисы

* **Redis Streams:** Основной брокер сообщений для задач
* **StatsD:** Сбор и отправка метрик
* **Jaeger:** Распределенное трейсинг
* **Loki:** Централизованное логирование

##### Внутренние сервисы

* Темплейт не предполагает зависимостей от других микросервисов
* Каждый сгенерированный сервис полностью автономен

#### 2.4.4 Структура данных

```json
HealthResponse: {
  "status": "str - статус сервиса (healthy/unhealthy)",
  "timestamp": "str - ISO timestamp",
  "redis_connected": "bool - статус подключения к Redis",
  "version": "str - версия сервиса"
}
```

#### 2.4.5 База данных

**НЕ имеется. Все данные обрабатываются в памяти или через Redis Streams**

#### 2.4.6 Интеграции и внешние зависимости

* **Redis Streams:** основной брокер сообщений
* **StatsD:** отправка метрик производительности
* **Jaeger:** трейсинг HTTP запросов и задач
* **Loki:** структурированное логирование

### 2.5 Нефункциональные требования

#### 2.5.1 Производительность

* **RPS:** 100,000+ (предельная производительность)
* **Время отклика API:** < 1ms (202 Accepted)
* **Время обработки задач:** Зависит от реализации(предельно низкая)
* **Пропускная способность:** Ограничена только Redis Streams

#### 2.5.2 Масштабируемость

* **Горизонтальное масштабирование:** Unlimited replicas
* **Автоматическое масштабирование:** По метрикам CPU/Memory
* **Максимальная нагрузка:** Ограничена только инфраструктурой

#### 2.5.3 Надежность

* **Доступность:** 99.9%+
* **Обработка ошибок:** Graceful degradation
* **Retry‑политика:** Exponential backoff в Redis Streams
* **Graceful shutdown:** Завершение всех фоновых задач

#### 2.5.4 Безопасность

* **Аутентификация:** Не предусмотрена в базовом темплейте
* **Авторизация:** Не предусмотрена в базовом темплейте
* **Валидация входных данных:** Pydantic schemas
* **Rate limiting:** На уровне инфраструктуры

#### 2.5.5 Специфические бизнес‑правила

* **Все задачи должны быть завершены перед завершением работы микросервиса**
* Все задачи обрабатываются равноценно (без приоритетов)
* Гарантия обработки не предоставляется (fire-and-forget)
* Мгновенный ответ API имеет наивысший приоритет
* Все операции должны быть идемпотентными
* Graceful shutdown обязателен

#### 2.5.6 Специфические ограничения

* **Минимальная задержка ответа** - главный приоритет
* **Все задачи равноценны** - нет системы приоритетов
* **Fire-and-forget** - нет гарантии обработки
* **Stateless** - сервис не хранит состояние между запросами
* **In-memory processing** - нет использования БД

### 2.6 Конфигурация

#### 2.6.1 Переменные окружения

```bash
# Основные настройки
SERVICE_NAME=generated-service
SERVICE_VERSION=1.0.0
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0

# Redis настройки
REDIS_URL=redis://localhost:6379
REDIS_STREAM_NAME=tasks:stream
REDIS_CONSUMER_GROUP=processors
REDIS_CONSUMER_NAME=worker

# Мониторинг
STATSD_HOST=localhost
STATSD_PORT=8125
STATSD_PREFIX=microservice

JAEGER_ENDPOINT=http://localhost:14268/api/traces
JAEGER_SERVICE_NAME=generated-service

LOKI_ENDPOINT=http://localhost:3100/loki/api/v1/push

# Производительность
UVLOOP_ENABLED=true
WORKER_PROCESSES=auto
MAX_CONCURRENT_TASKS=1000
TASK_TIMEOUT=30
MAX_PAYLOAD_SIZE=1048576

# Graceful shutdown
SHUTDOWN_TIMEOUT=30
```

#### 2.6.2 Конфигурационные файлы

* **pyproject.toml:** Зависимости и метаданные
* **docker-compose.yml:** Локальная разработка с Redis
* **Dockerfile:** Оптимизированный образ для production
* **noxfile.py:** Команды для CI/CD

### 2.7 Мониторинг и логирование

#### 2.7.1 Метрики (StatsD)

* **request_count:** Количество HTTP запросов
* **request_duration:** Время обработки запросов
* **task_queue_size:** Размер очереди задач
* **task_processing_time:** Время обработки задач
* **error_rate:** Процент ошибок
* **memory_usage:** Использование памяти
* **cpu_usage:** Использование CPU

##### Специфичные метрики темплейта

* **gpu_usage_per_task_avg:** Среднее использование GPU на задачу
* **gpu_usage_per_task_max:** Максимальное использование GPU на задачу
* **gpu_usage_per_task_min:** Минимальное использование GPU на задачу
* **memory_usage_per_task_avg:** Среднее использование памяти на задачу
* **memory_usage_per_task_max:** Максимальное использование памяти на задачу
* **memory_usage_per_task_min:** Минимальное использование памяти на задачу

#### 2.7.2 Логирование (Loki)

* **Уровни:** DEBUG/INFO/WARNING/ERROR/CRITICAL
* **Формат:** JSON structured logs
* **Поля:** timestamp, level, message, task_id, trace_id
* **Корреляция:** По task_id и trace_id

#### 2.7.3 Трейсинг (Jaeger)

* **Spans:** HTTP request, task processing, Redis operations
* **Correlation:** Trace-id в заголовках HTTP
* **Sampling:** 100% для **ВСЕХ** операций

##### Специфичные трейсы темплейта

* **api_request_span:** Полный цикл HTTP запроса
* **task_processing_span:** Асинхронная обработка задачи
* **redis_operations_span:** Операции с Redis Streams

#### 2.7.4 Health checks

* **Endpoint:** `/health`
* **Интервал:** 10 секунд
* **Критерии:** Redis connectivity, Memory usage < 90%

### 2.8 Тестирование

#### 2.8.1 Типы тестов

* **Unit:** 80%+ coverage
* **Integration:** Redis Streams, HTTP API
* **Load:** Предельная нагрузка RPS
* **Performance:** Response time < 1ms

#### 2.8.2 Тестовые сценарии

* **Мгновенный ответ:** API должен отвечать < 1ms
* **Обработка задач:** Задачи должны обрабатываться асинхронно
* **Graceful shutdown:** Все задачи должны завершиться корректно
* **High load:** Устойчивость к предельной нагрузке
* **Redis failure:** Graceful degradation при отключении Redis
* **Memory pressure:** Поведение при нехватке памяти

### 2.9 Развертывание

#### 2.9.1 Containerization

* **Base image:** python:3.13-slim
* **Multi-stage build:** Для минимизации размера
* **Ports:** 8000 (HTTP), 8080 (metrics)
* **Health checks:** Docker и Kubernetes probes

#### 2.9.2 Orchestration

* **Docker Compose:** Для локальной разработки
* **Kubernetes:** Готовые манифесты в темплейте
* **Resources:** CPU: 100m-2000m, Memory: 256Mi-2Gi
* **Replicas:** 1-1000 (горизонтальное масштабирование)

### 2.10 Messaging & Task Queue

#### 2.10.1 Redis Streams Configuration

* **Stream name:** `tasks:stream`
* **Consumer group:** `processors`
* **Consumer name:** `${HOSTNAME}:${PID}`
* **Max length:** 100,000 messages
* **Retention:** 1 hour

#### 2.10.2 Message Format

```json
{
  "task_id": "uuid4",
  "timestamp": "2025-01-01T00:00:00Z",
  "payload": {
    "data": "any",
    "metadata": {}
  },
  "trace_context": {
    "trace_id": "jaeger-trace-id",
    "span_id": "jaeger-span-id"
  }
}
```

#### 2.10.3 Fire-and-forget Processing

* **Немедленный ответ:** 202 Accepted
* **Асинхронная обработка:** Через Redis Streams
* **Без гарантий:** Best-effort delivery
* **Без приоритетов:** Все задачи равноценны

#### 2.10.4 Error Handling

* **Retry policy:** Exponential backoff (max 3 attempts)
* **Dead letter queue:** Для неуспешных задач
* **Circuit breaker:** При высоком проценте ошибок
* **Graceful degradation:** Сброс задач при перегрузке

#### 2.10.5 Graceful Shutdown

* **SIGTERM handling:** Остановка приема новых задач
* **Task completion:** Завершение всех активных задач
* **Timeout:** 30 секунд на завершение
* **Force kill:** SIGKILL после timeout

### 2.11 Дополнительные требования

#### 2.11.1 Особые условия

* **Минимальная задержка** - главный приоритет
* **Максимальная производительность** - основная цель
* **Горизонтальное масштабирование** - без ограничений
* **Отказоустойчивость** - graceful degradation
* **Качественность README** - обязательна с детальными инструкциями
* **Отсутствие лишнего кода** - только необходимый функционал

#### 2.11.2 Ограничения

* **Нет базы данных** - только in-memory processing
* **Нет приоритетов** - все задачи равноценны
* **Fire-and-forget** - нет гарантии обработки
* **Нет аутентификации** - добавляется при необходимости
* **Нет бизнес-логики** - только базовый функционал

#### 2.11.3 Предположения

* **Redis Streams** всегда доступен
* **Высокая нагрузка** - постоянное состояние
* **Stateless** - сервис не хранит состояние
* **Горизонтальное масштабирование** - основной способ увеличения производительности
* **Мониторинг** - всегда включен

### 2.12 Критерии приемки

* [ ] API отвечает менее чем за 1ms (202 Accepted)
* [ ] Все задачи обрабатываются асинхронно через Redis Streams
* [ ] Graceful shutdown завершает все активные задачи
* [ ] Мониторинг работает (StatsD, Loki, Jaeger)
* [ ] Темплейт генерирует работающий сервис
* [ ] Load testing показывает предельную производительность
* [ ] Нет блокирующих операций в API handlers
* [ ] Покрытие тестами > 80%
* [ ] Docker и Docker Compose работают корректно
* [ ] Документация полная и понятная
* [ ] Все метрики GPU и памяти собираются корректно

## 3. ПРИМЕЧАНИЯ ДЛЯ РАЗРАБОТЧИКОВ

### 3.1 Начало работы с темплейтом

1. Установите cookiecutter: `pip install cookiecutter`
2. Создайте проект: `cookiecutter gh:your-org/cookiecutter-high-performance-pyms`
3. Заполните переменные темплейта
4. Перейдите в созданную директорию
5. `uv sync` – установите зависимости
6. `docker-compose up -d` – запустите Redis
7. `uv run pytest` – убедитесь, что тесты проходят
8. `uv run src/{{cookiecutter.python_package_name}}/main.py` – запустите сервис

### 3.2 Архитектурные принципы

* **Немедленный ответ:** Всегда возвращайте 202 Accepted
* **Асинхронность:** Используйте asyncio + uvloop
* **Stateless:** Не храните состояние в сервисе
* **Circuit breaker:** Защищайтесь от каскадных отказов
* **Graceful shutdown:** Корректно завершайте фоновые задачи

### 3.3 Полезные ссылки

* [Cookiecutter документация](https://cookiecutter.readthedocs.io/)
* [Starlette документация](https://www.starlette.io/)
* [Uvicorn руководство](https://www.uvicorn.org/)
* [Redis Streams](https://redis.io/docs/data-types/streams/)
* [OpenTelemetry Python](https://opentelemetry-python.readthedocs.io/)
* [Grafana Loki](https://grafana.com/docs/loki/)
* [StatsD Protocol](https://github.com/statsd/statsd/blob/master/docs/metric_types.md)

