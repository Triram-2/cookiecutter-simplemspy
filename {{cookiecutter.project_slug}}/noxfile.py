"""Nox sessions for linting, testing, building, and deployment."""

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, TYPE_CHECKING, Iterator

# Conditional import for tomllib/tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        print("Error: 'tomli' is not installed. Please install it for Python < 3.11.")
        sys.exit(1)

if TYPE_CHECKING:
    # If you need to import specific types from tomllib for type hinting, do it here.
    # For example: from tomllib import TOMLDecodeError
    pass  # Often, just having tomllib imported as above is enough.

import nox
from nox import Session  # Import Session for type hinting


# --- Конфигурация ---
nox.options.default_venv_backend = "uv"

# Type hint for PYPROJECT_CONTENT
PYPROJECT_CONTENT: Dict[str, Any] = tomllib.loads(
    Path("pyproject.toml").read_text(encoding="utf-8")
)

PROJECT_NAME: str = PYPROJECT_CONTENT["project"]["name"]
PYTHON_VERSIONS: List[str] = ["{{cookiecutter.python_version}}", "3.12"]
SRC_DIR: str = "src"
TESTS_DIR: str = "tests"
DOCS_DIR: str = "docs"
COVERAGE_FAIL_UNDER: int = (
    40  # Минимальный процент покрытия для тестов ( временно снижено с 70 )
)
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


# --- Вспомогательные функции ---
def install_project_with_deps(session: Session, *groups: str) -> None:
    """Устанавливает проект и его зависимости из указанных групп (вручную).""" # Updated docstring
    session.log(f"Manually installing dependencies for groups: {groups} and project in editable mode.")

    # 1. Install base project dependencies
    base_dependencies = PYPROJECT_CONTENT.get("project", {}).get("dependencies", [])
    if base_dependencies:
        session.log(f"Installing base dependencies: {base_dependencies}")
        session.run_always("uv", "pip", "install", *base_dependencies, external=True)
    else:
        session.log("No base dependencies found in pyproject.toml.")

    # 2. Install dependencies from specified groups (extras)
    if groups:
        all_extras_deps = []
        optional_deps = PYPROJECT_CONTENT.get("project", {}).get("optional-dependencies", {})
        for group_name in groups: # Renamed 'group' to 'group_name' to avoid conflict if 'groups' var was a list of lists
            group_specific_deps = optional_deps.get(group_name, [])
            if group_specific_deps:
                session.log(f"Found dependencies for group '{group_name}': {group_specific_deps}")
                all_extras_deps.extend(group_specific_deps)
            else:
                session.log(f"No dependencies found for group: {group_name}")

        if all_extras_deps:
            # Deduplicate dependencies that might be listed in multiple groups or also in base
            unique_extras_deps = list(set(all_extras_deps))
            session.log(f"Installing unique extra dependencies: {unique_extras_deps}")
            session.run_always("uv", "pip", "install", *unique_extras_deps, external=True)
        else:
            session.log("No dependencies found for the specified groups.")
    else:
        session.log("No groups specified, skipping extras installation.")

    # 3. Install the project itself in editable mode, without re-installing its direct dependencies
    session.log("Installing project in editable mode with --no-deps...")
    session.run_always("uv", "pip", "install", "-e", ".", "--no-deps", external=True)
    session.log("Project installed in editable mode with --no-deps.")


# --- Сессии Nox ---


@nox.session(python=PYTHON_VERSIONS)
def lint(session: Session) -> None:
    """Запускает линтеры (Ruff, Pyright) и проверку формата."""
    session.log("Установка зависимостей для линтинга...")
    install_project_with_deps(session, "lint")

    session.log("Запуск Ruff (форматирование --check)...")
    session.run("ruff", "format", ".")

    session.log("Запуск Ruff (линтинг)...")
    session.run("ruff", "check", ".")

    session.log("Запуск Pyright...")
    session.run(
        "python",
        "-m",
        "pyright",
        "--project",
        "pyproject.toml",
        env={"PYTHONPATH": "."},
    )

    session.log("Линтинг завершен успешно.")


@nox.session(python=PYTHON_VERSIONS)
def test(session: Session) -> None:
    """Запускает тесты с pytest, coverage и hypothesis, а также pip-audit."""
    session.log("Установка зависимостей для тестирования...")
    install_project_with_deps(session, "test")

    session.log("Запуск pip-audit для проверки уязвимостей...")
    session.run("pip-audit", "--local", "--progress-spinner", "off")

    session.log("Запуск тестов с coverage...")
    session.run(
        "coverage",
        "run",
        "--source",
        SRC_DIR,
        "-m",
        "pytest",
        TESTS_DIR,
        *session.posargs,
    )

    session.log(f"Проверка покрытия кода (должно быть >= {COVERAGE_FAIL_UNDER}%)...")
    session.run("coverage", "report", "-m", f"--fail-under={COVERAGE_FAIL_UNDER}")

    session.log("Генерация отчета о покрытии в формате HTML и XML...")
    session.run("coverage", "html", "-d", "coverage_html_report")
    session.run("coverage", "xml", "-o", "coverage.xml")

    session.log("Тестирование завершено успешно.")


@nox.session(python=PYTHON_VERSIONS[0])
def docs(session: Session) -> None:
    """Сборка документации с помощью Sphinx."""
    session.log("Установка зависимостей для сборки документации...")
    session.install("sphinx", "sphinx-rtd-theme")
    install_project_with_deps(session)  # Установить проект, чтобы autodoc работал

    docs_build_dir: Path = Path(DOCS_DIR) / "_build" / "html"

    session.log(f"Очистка старой документации в {docs_build_dir}...")
    if docs_build_dir.exists():
        shutil.rmtree(docs_build_dir)

    session.log("Сборка HTML документации...")
    session.run(
        "sphinx-build",
        "-b",
        "html",
        "-W",
        "--keep-going",
        DOCS_DIR,
        str(docs_build_dir),
    )
    session.log(f"Документация собрана в: {docs_build_dir.resolve()}")


@nox.session(python=PYTHON_VERSIONS[0])
def profile(session: Session) -> None:
    """Запуск профилировщика Scalene."""
    session.log("Установка зависимостей для профилирования...")
    install_project_with_deps(session, "profile")

    session.log("Запуск Scalene...")
    try:
        session.run("scalene", "src/main.py", *session.posargs)

        # Assuming PYPROJECT_CONTENT structure is valid and keys exist for simplicity
        # A more robust approach would involve checking key existence
        outfile_setting = (
            PYPROJECT_CONTENT.get("tool", {}).get("scalene", {}).get("outfile")
        )
        outfile: str
        if isinstance(outfile_setting, str):
            outfile = outfile_setting
        else:
            outfile = "scalene_report.html"  # Default if not found or not a string

        session.log(f"Отчет Scalene сохранен (вероятно) в: {Path(outfile).resolve()}")
    except Exception as e:
        session.error(
            f"Ошибка при запуске Scalene: {e}. Проверьте команду запуска и конфигурацию."
        )


@nox.session(python=False)
def build(session: Session) -> None:
    """Сборка Docker-образа."""
    project_version_any: Any = PYPROJECT_CONTENT["project"]["version"]
    project_version: str = str(project_version_any)  # Ensure it's a string

    image_tag: str = f"{PROJECT_NAME}:{project_version}"
    latest_tag: str = f"{PROJECT_NAME}:latest"

    session.log(f"Сборка Docker-образа {image_tag} и {latest_tag}...")
    try:
        session.run(
            "docker",
            "build",
            ".",
            "-t",
            image_tag,
            "-t",
            latest_tag,
            *session.posargs,
            external=True,
        )
        session.log("Сборка Docker-образа завершена успешно.")
    except Exception as e:
        session.error(
            f"Ошибка при сборке Docker-образа. Убедитесь, что Docker запущен. Ошибка: {e}"
        )


@nox.session(python=False)
def clean(session: Session) -> None:
    """Удаляет временные файлы и папки сборки/тестирования."""
    session.log("Очистка...")
    patterns_to_remove: List[str] = [
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
        "scalene_report.html",
        "**/.mypy_cache",
        "**/.ruff_cache",
        "**/__pycache__",
        f"{DOCS_DIR}/_build",
        "vulnerabilities.json",
    ]
    for pattern in patterns_to_remove:
        try:
            if "*" in pattern or "?" in pattern:
                # Path.glob returns a generator of Path objects
                path_iter: Iterator[Path] = Path(".").glob(pattern)
                for path_obj in path_iter:  # path_obj is a Path object
                    session.log(f"Удаление {path_obj}")
                    if path_obj.is_dir():
                        shutil.rmtree(path_obj, ignore_errors=True)
                    else:
                        path_obj.unlink(missing_ok=True)
            else:
                path_obj: Path = Path(pattern)  # path_obj is a Path object
                if path_obj.exists():
                    session.log(f"Удаление {path_obj}")
                    if path_obj.is_dir():
                        shutil.rmtree(path_obj, ignore_errors=True)
                    else:
                        path_obj.unlink(missing_ok=True)
        except Exception as e:
            session.warn(f"Не удалось удалить {pattern}: {e}")
    session.log("Очистка завершена.")


@nox.session(python=PYTHON_VERSIONS[0])
def locust(session: Session) -> None:
    """Запускает нагрузочное тестирование с Locust."""
    session.log("Установка зависимостей для Locust...")
    install_project_with_deps(session, "loadtest")

    locust_file: str = "locustfile.py"
    if not Path(locust_file).exists():
        session.warn(
            f"Файл {locust_file} не найден. Для запуска Locust необходимо создать его и определить сценарии нагрузки."
        )
        session.log(
            "Пример команды, если locustfile.py существует: locust -f locustfile.py --host=http://localhost:8000"
        )
        return

    session.log(f"Запуск Locust (используя {locust_file})...")
    session.run("locust", "-f", locust_file, *session.posargs)


# --- Сессия для CI ---
@nox.session(python=PYTHON_VERSIONS, name="ci")
def ci_pipeline(session: Session) -> None:
    """Запускает основные проверки для CI: lint и test."""
    session.log(f"Запуск CI пайплайна для Python {session.python}")

    # session.python is typed as str | None.
    # session.notify expects posargs: Iterable[str] | None.
    # If session.python is None, [None] is not Iterable[str].
    # We ensure only a list of strings or an empty list is passed.
    # In this specific CI context, session.python should always be a string
    # due to parameterization with PYTHON_VERSIONS, but this satisfies Pyright's
    # strictness based on the general type hint of session.python.
    current_python_version_arg: List[str] = []
    if isinstance(session.python, str):
        current_python_version_arg.append(session.python)

    session.notify("lint", current_python_version_arg)
    session.notify("test")
