"""Exercise the temporary home folder tests/conftest.py gives every test run before brachify is imported."""
from __future__ import annotations

import tempfile
from pathlib import Path


def test_brachify_user_folder_is_inside_the_temporary_folder() -> None:
    """Check classes.info.USER_PATH, fixed when brachify is first imported, is inside the system temp folder.

    Fails if a test module imports brachify before HOME is redirected, which makes USER_PATH the
    developer's real ~/brachify. The template fixtures then delete the developer's saved cylinder,
    tandem and needle templates, the run writes into their app.log, and parallel workers race on
    the one shared library file.
    """
    from classes.info import USER_PATH

    assert Path(tempfile.gettempdir()).resolve() in USER_PATH.resolve().parents
