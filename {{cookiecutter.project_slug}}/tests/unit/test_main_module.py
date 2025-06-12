from src import main as main_module
from src.core.config import AppSettings


def test_main_module_imports_and_attributes():
    assert hasattr(main_module, "settings")
    assert isinstance(main_module.settings, AppSettings)
    assert hasattr(main_module, "log")
