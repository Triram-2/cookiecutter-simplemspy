from loguru import logger as loguru_logger
import logging
import json
from typing import Any

from {{cookiecutter.python_package_name}}.core.logging_config import get_logger, setup_initial_logger, InterceptHandler
from {{cookiecutter.python_package_name}}.core import config


def test_should_post_logs_to_loki(monkeypatch):
    posted: dict[str, Any] = {}

    def fake_post(url: str, *, json: Any) -> None:  # type: ignore[override]
        posted["url"] = url
        posted["json"] = json

    monkeypatch.setattr(config.settings.log, "loki_endpoint", "http://loki:3100/loki/api/v1/push")
    monkeypatch.setattr("httpx.post", fake_post)

    setup_initial_logger()
    logger = get_logger("loki_test")
    logger.info("hello")

    assert posted["url"].endswith("/loki/api/v1/push")
    assert posted["json"]["streams"][0]["stream"]["app"] == config.settings.service.name


def test_get_logger_returns_bound_logger():
    logger_instance = get_logger("test_module")
    assert hasattr(logger_instance, "info")
    assert hasattr(logger_instance, "error")


def test_setup_initial_logger_configures_levels_and_handler():
    setup_initial_logger()

    assert loguru_logger.level("INFO").name == "INFO"
    assert loguru_logger.level("ERROR").name == "ERROR"

    root_std_logger = logging.getLogger()
    assert any(isinstance(h, InterceptHandler) for h in root_std_logger.handlers)


def test_get_logger_with_empty_name():
    logger_instance = get_logger("")
    assert hasattr(logger_instance, "info")


def test_logger_outputs_json(capsys):
    setup_initial_logger()
    loguru_logger.info("json message")
    captured = capsys.readouterr().err.strip().splitlines()[-1]
    data = json.loads(captured)
    assert data["record"]["message"] == "json message"
    assert data["record"]["level"]["name"] == "INFO"


# Note: Testing file creation/writing by get_logger is more complex and
# would require mocking file system operations or cleaning up created files.
# These basic tests primarily cover function calls and some configuration aspects.
