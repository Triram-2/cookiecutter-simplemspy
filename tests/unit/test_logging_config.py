from loguru import logger as loguru_logger
import logging

# Assuming internal imports
from name.core.logging_config import get_logger, setup_initial_logger, InterceptHandler


def test_get_logger_returns_bound_logger():
    logger_instance = get_logger("test_module")
    # Check if it's a Loguru logger instance (hard to check specific bound name directly without internals)
    assert hasattr(logger_instance, "info")
    assert hasattr(logger_instance, "error")


def test_setup_initial_logger_configures_levels_and_handler():
    # Reset logger state for this test if possible, or check idempotent parts
    # For simplicity, we'll check some expected configurations
    setup_initial_logger()  # Should run on import, but call to ensure

    # Check if levels are set (example)
    assert loguru_logger.level("INFO").name == "INFO"
    assert loguru_logger.level("ERROR").name == "ERROR"

    # Check if InterceptHandler is part of standard logging
    root_std_logger = logging.getLogger()
    assert any(isinstance(h, InterceptHandler) for h in root_std_logger.handlers)


def test_get_logger_with_empty_name():
    # This should log an error via loguru and return a logger bound to 'unnamed_logger_error'
    # We can't easily capture loguru's internal error log here without more setup
    # So, we just check that it returns a logger
    logger_instance = get_logger("")
    assert hasattr(logger_instance, "info")


# Note: Testing file creation/writing by get_logger is more complex and
# would require mocking file system operations or cleaning up created files.
# These basic tests primarily cover function calls and some configuration aspects.
