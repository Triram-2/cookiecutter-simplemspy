from loguru import logger as loguru_logger
import logging

from {{cookiecutter.python_package_name}}.core.logging_config import get_logger, setup_initial_logger, InterceptHandler


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


# Note: Testing file creation/writing by get_logger is more complex and
# would require mocking file system operations or cleaning up created files.
# These basic tests primarily cover function calls and some configuration aspects.
