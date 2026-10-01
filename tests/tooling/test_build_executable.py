import importlib

import pytest

import build_executable


@pytest.mark.parametrize("module_name", build_executable.HIDDEN_IMPORTS)
def test_hidden_import_exists_in_the_environment(module_name: str) -> None:
    """Import each module that build_executable.py tells PyInstaller to bundle.

    Runs once per entry in HIDDEN_IMPORTS and fails with ModuleNotFoundError if that module
    cannot be imported in the current conda environment. PyInstaller only logs
    "ERROR: Hidden import ... not found" for a missing module and still builds with exit 0,
    so a module renamed upstream (as pydicom 3 did with pydicom.encoders) would silently drop
    out of brachify.exe. This test makes that failure loud.
    """
    importlib.import_module(module_name)
