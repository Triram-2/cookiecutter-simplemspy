# Assuming internal imports (src.main needs to be importable)
# If src.main relies on 'name.api' which is now 'api', it should be fine.
from name import main as main_module  # from src.main
from name.core.config import AppSettings


def test_main_module_imports_and_attributes():
    assert hasattr(main_module, "settings")
    assert isinstance(main_module.settings, AppSettings)
    assert hasattr(main_module, "log")  # Check for the logger instance
    # The actual FastAPI app is usually imported from api module, not defined in src.main directly.
    # If src.main re-exports the app, that could be tested:
    # assert hasattr(main_module, "app")
