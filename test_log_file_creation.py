import sys
import time  # Added for sleep

# Ensure src directory is in path if running from /app
sys.path.insert(0, "./src")

try:
    print(
        "--- [Test Script] Attempting to import get_logger from src.core.logging_config ---"
    )
    # We don't need the global_loguru_logger instance directly if we are not calling remove() on it
    from core.logging_config import get_logger

    print("--- [Test Script] Imports successful ---")

    # Get a logger instance
    log_name = "test_file_log"
    print(f"--- [Test Script] Calling get_logger('{log_name}') ---")
    file_test_logger = get_logger(log_name)
    print(f"--- [Test Script] get_logger('{log_name}') returned ---")

    # Log some messages
    print("--- [Test Script] Logging messages ---")
    file_test_logger.info("This is an INFO message for test_file_log.")
    file_test_logger.warning("This is a WARNING message for test_file_log.")
    file_test_logger.error("This is an ERROR message for test_file_log.")
    print("--- [Test Script] Messages logged ---")

    # Add a standard library log to test interception for this specific name
    import logging

    std_test_logger = logging.getLogger(log_name)  # Use the same name
    std_test_logger.setLevel(logging.INFO)
    print(
        f"--- [Test Script] Logging standard library message for logger '{log_name}' ---"
    )
    std_test_logger.info(
        "This is a standard library INFO message for test_file_log, to be intercepted."
    )
    print("--- [Test Script] Standard library message logged ---")

    # Give time for enqueued logs to be written
    print("--- [Test Script] Sleeping for 1 second to allow log queue to flush ---")
    time.sleep(1)
    print("--- [Test Script] Sleep finished ---")

    # The global logger.remove() was removed from here.
    # setup_initial_logger() already ran and did its own logger.remove() and add console.
    # get_logger() added file handlers. We want to see if they wrote before script ends.

    print("--- [Test Script] Execution finished ---")

except Exception as e:
    print(f"--- [Test Script] ERROR: {e} ---")
    import traceback

    traceback.print_exc()
