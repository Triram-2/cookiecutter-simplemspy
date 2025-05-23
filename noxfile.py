"""Nox sessions for linting, testing, building, and deployment."""
import os
import shutil
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib # type: ignore

from pathlib import Path

import nox


# --- Конфигурация ---
nox.options.default_venv_backend = "uv"
PYPROJECT_CONTENT = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
PROJECT_NAME = PYPROJECT_CONTENT["project"]["name"]
PYTHON_VERSIONS = ["3.13", "3.12"]
SRC_DIR = "src"
TESTS_DIR = "tests"
DOCS_DIR = "docs"
COVERAGE_FAIL_UNDER = 70 # Минимальный процент покрытия для тестов
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# --- Вспомогательные функции ---
def install_project_with_deps(session: nox.Session, *groups: str) -> None:
    """Устанавливает проект и его зависимости из указанных групп."""
    install_args = ["-e", f".[{','.join(groups)}]"] if groups else ["-e", "."]
    session.run_always("uv", "pip", "install", *install_args, external=True)

# --- Сессии Nox ---

@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Запускает линтеры (Ruff, Pyright) и проверку формата."""
    session.log("Установка зависимостей для линтинга...")
    session.install("ruff", "pyright")

    session.log("Запуск Ruff (форматирование --check)...")
    session.run("ruff", "format", ".", "--check")

    session.log("Запуск Ruff (линтинг)...")
    session.run("ruff", "check", ".")

    session.log("Запуск Pyright...")
    session.run("pyright")

    session.log("Линтинг завершен успешно.")


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Запускает тесты с pytest, coverage и hypothesis, а также pip-audit."""
    session.log("Установка зависимостей для тестирования (включая 'audit' для pip-audit)...")
    install_project_with_deps(session, "test", "audit") # Добавлена группа "audit"

    session.log("Запуск pip-audit для проверки уязвимостей...")
    session.run("python", "-m", "pip_audit", "--local", "--progress-spinner", "off")

    session.log("Запуск тестов с coverage...")
    session.run(
        "coverage",
        "run",
        "--source", SRC_DIR,
        "-m", "pytest",
        TESTS_DIR,
        *session.posargs
    )

    session.log(f"Проверка покрытия кода (должно быть >= {COVERAGE_FAIL_UNDER}%)...")
    session.run(
        "coverage",
        "report",
        "-m",
        f"--fail-under={COVERAGE_FAIL_UNDER}"
    )

    session.log("Генерация отчета о покрытии в формате HTML и XML...")
    session.run("coverage", "html", "-d", "coverage_html_report")
    session.run("coverage", "xml", "-o", "coverage.xml")

    session.log("Тестирование завершено успешно.")


@nox.session(python=PYTHON_VERSIONS[0])
def docs(session: nox.Session) -> None:
    """Сборка документации с помощью Sphinx."""
    session.log("Установка зависимостей для сборки документации...")
    session.install("sphinx", "sphinx-rtd-theme")
    install_project_with_deps(session) # Установить проект, чтобы autodoc работал

    docs_build_dir = Path(DOCS_DIR) / "_build" / "html"

    session.log(f"Очистка старой документации в {docs_build_dir}...")
    if docs_build_dir.exists():
        shutil.rmtree(docs_build_dir)

    session.log("Сборка HTML документации...")
    # Команда сборки Sphinx
    session.run(
        "sphinx-build",
        "-b", "html",       # Формат сборки (html)
        "-W",               # Превращать предупреждения в ошибки
        "--keep-going",     # Продолжать сборку при ошибках (если нужно)
        DOCS_DIR,           # Исходная директория документации
        str(docs_build_dir) # Выходная директория
    )
    session.log(f"Документация собрана в: {docs_build_dir.resolve()}")


@nox.session(python=PYTHON_VERSIONS[0])
def profile(session: nox.Session) -> None:
    """Запуск профилировщика Scalene."""
    session.log("Установка зависимостей для профилирования...")
    # session.install("scalene") # Scalene теперь в project.optional-dependencies.profile
    install_project_with_deps(session, "profile") # Устанавливаем зависимости профилирования, включая сам проект

    session.log("Запуск Scalene...")
    # Комментарий: Текущая команда `scalene src/main.py` (или `scalene src/main.py run`) запускает Uvicorn через src/main.py.
    # Это профилирует всё приложение, включая Uvicorn, что может быть не всегда желаемым результатом.
    # Для профилирования конкретных частей бизнес-логики или отдельных функций,
    # может потребоваться создание специальных скриптов-оберток или изменение команды запуска.
    # Например, `scalene -m your_module_to_profile` или `python -m scalene --program your_script.py`.
    # Также, `*session.posargs` здесь может быть нерелевантным, если `src/main.py` не принимает доп. аргументы.
    try:
        # Попытка прочитать точку входа или параметры из pyproject.toml, если они там есть
        # Для данного шаблона, мы просто используем src/main.py как пример
        # и предполагаем, что пользователь адаптирует это под свои нужды.
        # Пример: session.run("scalene", "src/main.py", *session.posargs) 
        # Если src/main.py не принимает 'run', а просто запускает uvicorn, то можно так:
        # session.run("scalene", "-m", "uvicorn", "src.api:app", "--host", settings.app_host, "--port", str(settings.app_port))
        # Для простоты примера оставим вызов src/main.py, предполагая, что он запускает Uvicorn
        session.run("scalene", "src/main.py", *session.posargs)

        outfile = PYPROJECT_CONTENT.get("tool", {}).get("scalene", {}).get("outfile", "scalene_report.html")
        session.log(f"Отчет Scalene сохранен (вероятно) в: {Path(outfile).resolve()}")
    except Exception as e:
        session.error(f"Ошибка при запуске Scalene: {e}. Проверьте команду запуска и конфигурацию.")


@nox.session(python=False)
def build(session: nox.Session) -> None:
    """Сборка Docker-образа."""
    project_version = PYPROJECT_CONTENT["project"]["version"]
    image_tag = f"{PROJECT_NAME}:{project_version}"
    latest_tag = f"{PROJECT_NAME}:latest"

    session.log(f"Сборка Docker-образа {image_tag} и {latest_tag}...")
    try:
        session.run(
            "docker",
            "build",
            ".",
            "-t", image_tag,
            "-t", latest_tag,
            # Добавьте сюда другие флаги docker build, если нужно (--build-arg, --platform и т.д.)
            *session.posargs,
            external=True # Указываем, что docker - внешняя команда
        )
        session.log("Сборка Docker-образа завершена успешно.")
    except Exception as e:
         session.error(f"Ошибка при сборке Docker-образа. Убедитесь, что Docker запущен. Ошибка: {e}")


@nox.session(python=False)
def clean(session: nox.Session) -> None:
    """Удаляет временные файлы и папки сборки/тестирования."""
    session.log("Очистка...")
    patterns_to_remove = [
        "dist",
        "build",
        "*.egg-info",
        ".nox",
        ".pytest_cache",
        ".coverage",
        "coverage.xml",
        "coverage_html_report",
        "*.prof",
        "profile_output",
        "scalene_report.html", # И другие файлы отчетов
        "**/.mypy_cache",
        "**/.ruff_cache",
        "**/__pycache__",
        f"{DOCS_DIR}/_build",
        "vulnerabilities.json" # Отчет pip-audit
    ]
    for pattern in patterns_to_remove:
        try:
            if "*" in pattern or "?" in pattern: # Используем glob для шаблонов
                 for path in Path(".").glob(pattern):
                     session.log(f"Удаление {path}")
                     if path.is_dir():
                         shutil.rmtree(path, ignore_errors=True)
                     else:
                         path.unlink(missing_ok=True)
            else: # Прямое удаление файла или папки
                path = Path(pattern)
                if path.exists():
                    session.log(f"Удаление {path}")
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        path.unlink(missing_ok=True)
        except Exception as e:
            session.warn(f"Не удалось удалить {pattern}: {e}")
    session.log("Очистка завершена.")


@nox.session(python=PYTHON_VERSIONS[0])
def locust(session: nox.Session) -> None:
     """Запускает нагрузочное тестирование с Locust."""
     session.log("Установка зависимостей для Locust...")
     install_project_with_deps(session, "loadtest") # locust теперь в loadtest группе

     # Комментарий: Убедитесь, что файл `locustfile.py` существует в корне проекта
     # и содержит ваши сценарии нагрузочного тестирования.
     # Этот файл должен быть создан пользователем шаблона.
     locust_file = "locustfile.py"
     if not Path(locust_file).exists():
         session.warn(f"Файл {locust_file} не найден. Для запуска Locust необходимо создать его и определить сценарии нагрузки.")
         session.log("Пример команды, если locustfile.py существует: locust -f locustfile.py --host=http://localhost:8000")
         # Можно завершить сессию, если файл не найден, или просто предупредить.
         # Для шаблона лучше просто предупредить.
         return 

     session.log(f"Запуск Locust (используя {locust_file})...")
     # Пример команды: locust -f locustfile.py --host=http://localhost:8000 (хост можно передать через posargs)
     # session.posargs могут включать, например, --host, --users, --spawn-rate
     session.run("locust", "-f", locust_file, *session.posargs)


# --- Сессия для CI ---
# Эта сессия просто запускает другие сессии последовательно
@nox.session(python=PYTHON_VERSIONS, name="ci")
def ci_pipeline(session: nox.Session) -> None:
    """Запускает основные проверки для CI: lint и test."""
    session.log(f"Запуск CI пайплайна для Python {session.python}")
    session.notify("lint", [session.python])
    session.notify("test", [session.python])

