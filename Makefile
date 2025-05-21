# Команда Nox. Используем ?= чтобы можно было переопределить из командной строки,
# например: make test NOX=./path/to/nox
NOX ?= nox

# Аргументы, которые будут переданы в Nox сессию.
# Позволяет делать так: make test ARGS="-k my_specific_test --verbose"
ARGS ?=

# Цель по умолчанию: показать справку
.DEFAULT_GOAL := help

# Объявляем цели, которые не являются файлами.
# Это важно, чтобы make не искал файлы с именами lint, test и т.д.
.PHONY: help list lint test docs profile build clean locust ci install

# --- Основные команды ---

# Показать список доступных команд Makefile
help:
	@echo "Доступные команды Makefile (используют Nox под капотом):"
	@echo "  make help        - Показать это сообщение"
	@echo "  make list        - Показать список доступных сессий Nox"
	@echo "  make lint        - Запустить линтеры (Ruff, Pyright)"
	@echo "  make test        - Запустить тесты (pytest, coverage, pip-audit)"
	@echo "  make docs        - Собрать документацию (Sphinx)"
	@echo "  make profile     - Запустить профилировщик (Scalene)"
	@echo "  make build       - Собрать Docker-образ"
	@echo "  make clean       - Удалить временные файлы и папки"
	@echo "  make locust      - Запустить нагрузочное тестирование (Locust)"
	@echo "  make ci          - Запустить CI пайплайн (lint, test)"
	@echo ""
	@echo "Передача аргументов в сессию Nox: make <команда> ARGS=\"...\""
	@echo "Пример: make test ARGS=\"-k specific_test -v\""

# Показать список сессий Nox
list:
	@$(NOX) -l

# Линтинг
lint:
	@echo "==> Запуск линтеров через Nox..."
	@$(NOX) -s lint -- $(ARGS)

# Тестирование
test:
	@echo "==> Запуск тестов через Nox..."
	@$(NOX) -s test -- $(ARGS)

# Сборка документации
docs:
	@echo "==> Сборка документации через Nox..."
	@$(NOX) -s docs -- $(ARGS)

# Профилирование
profile:
	@echo "==> Запуск профилировщика через Nox..."
	@$(NOX) -s profile -- $(ARGS)

# Сборка (Docker)
build:
	@echo "==> Запуск сборки Docker-образа через Nox..."
	@$(NOX) -s build -- $(ARGS)

# Очистка
clean:
	@echo "==> Запуск очистки через Nox..."
	@$(NOX) -s clean -- $(ARGS)

# Нагрузочное тестирование
locust:
	@echo "==> Запуск Locust через Nox..."
	@$(NOX) -s locust -- $(ARGS)

# CI пайплайн
ci:
	@echo "==> Запуск CI пайплайна через Nox..."
	@$(NOX) -s ci -- $(ARGS)
