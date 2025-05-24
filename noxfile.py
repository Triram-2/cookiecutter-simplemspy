"""Nox sessions for linting, testing, building, and deployment."""

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, TYPE_CHECKING

# Conditional import for tomllib/tomli for type checking and compatibility
if sys.version_info >= (3, 11):
    import tomllib
else:
    # If Python < 3.11, tomli is expected to be available (e.g., via lint dependencies)
    # For type checkers, we can guard this import
    if TYPE_CHECKING:
        import tomli as tomllib # pyright: ignore [reportMissingModuleSource, reportGeneralTypeIssues]
    else:
        try:
            import tomli as tomllib
        except ModuleNotFoundError:
            # This case should ideally not be hit if tomli is a dependency for older Python versions
            print("Error: 'tomli' is not installed. Please install it for Python < 3.11.")
            sys.exit(1)


import nox
from nox import Session # Import Session for type hinting


# --- Конфигурация ---
nox.options.default_venv_backend = "uv"

# Type hint for PYPROJECT_CONTENT
PYPROJECT_CONTENT: Dict[str, Any] = tomllib.loads(
    Path("pyproject.toml").read_text(encoding="utf-8")
)

PROJECT_NAME: str = PYPROJECT_CONTENT["project"]["name"]
PYTHON_VERSIONS: List[str] = ["3.13", "3.12"]
SRC_DIR: str = "src"
TESTS_DIR: str = "tests"
DOCS_DIR: str = "docs"
COVERAGE_FAIL_UNDER: int = 70  # Минимальный процент покрытия для тестов
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


# --- Вспомогательные функции ---
def install_project_with_deps(session: Session, *groups: str) -> None:
    """Устанавливает проект и его зависимости из указанных групп."""
    install_args: List[str] = ["-e", f".[{','.join(groups)}]"] if groups else ["-e", "."]
    session.run_always("uv", "pip", "install", *install_args, external=True)


# --- Сессии Nox ---


@nox.session(python=PYTHON_VERSIONS)
def lint(session: Session) -> None:
    """Запускает линтеры (Ruff, Pyright) и проверку формата."""
    session.log("Установка зависимостей для линтинга...")
    install_project_with_deps(session, "lint")

    session.log("Запуск Ruff (форматирование --check)...")
    session.run("ruff", "format", ".", "--check")

    session.log("Запуск Ruff (линтинг)...")
    session.run("ruff", "check", ".")

    session.log("Запуск Pyright...")
    session.run("pyright")

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
        outfile_setting = PYPROJECT_CONTENT.get("tool", {}).get("scalene", {}).get("outfile")
        outfile: str
        if isinstance(outfile_setting, str):
            outfile = outfile_setting
        else:
            outfile = "scalene_report.html" # Default if not found or not a string
        
        session.log(f"Отчет Scalene сохранен (вероятно) в: {Path(outfile).resolve()}")
    except Exception as e:
        session.error(
            f"Ошибка при запуске Scalene: {e}. Проверьте команду запуска и конфигурацию."
        )


@nox.session(python=False)
def build(session: Session) -> None:
    """Сборка Docker-образа."""
    project_version_any: Any = PYPROJECT_CONTENT["project"]["version"]
    project_version: str = str(project_version_any) # Ensure it's a string

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
                for path_obj in path_iter: # path_obj is a Path object
                    session.log(f"Удаление {path_obj}")
                    if path_obj.is_dir():
                        shutil.rmtree(path_obj, ignore_errors=True)
                    else:
                        path_obj.unlink(missing_ok=True)
            else:
                path_obj: Path = Path(pattern) # path_obj is a Path object
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
    session.notify("lint", [session.python]) # session.python is str
    session.notify("test", [session.python])
