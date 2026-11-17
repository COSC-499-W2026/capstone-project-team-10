from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from classes.app import RadiotherapyApp

WINDOW_FIXTURES = frozenset({"channels_window", "tandem_window", "cylinder_window", "fresh_window", "anatomy_model"})


def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    """Mark every test that uses one of WINDOW_FIXTURES as slow. A hook, not a test.

    Each of those fixtures builds brachify's real main window, and channels_window and
    tandem_window also import a plan, which builds its needle channels in about 9 seconds. So
    `python -m pytest -m "not slow"` runs everything else in seconds, as a quick loop while
    writing a test. A plain `python -m pytest` still runs every test. A slow test that builds
    no window is marked by hand with @pytest.mark.slow. tests/tooling/test_slow_marker.py
    fails if a window test is left in the quick loop.
    """
    for item in items:
        if WINDOW_FIXTURES.intersection(item.fixturenames):
            item.add_marker(pytest.mark.slow)


def pytest_configure(config: pytest.Config) -> None:
    """Point HOME and USERPROFILE at a new temporary folder before any test module is imported. A hook, not a test.

    classes.info fixes ~/brachify when brachify is first imported, and several test modules
    import brachify at collection time, before any fixture runs. Without this, the run would
    use the developer's real ~/brachify: writing its app.log, reading its last config, and
    deleting its template libraries, which the template fixtures clear. Each process makes its
    own folder, so parallel workers never share a library file. The folder is removed at the
    end of the run. tests/tooling/test_test_home.py fails if brachify sees another home.
    """
    home = tempfile.mkdtemp(prefix="brachify-test-home-")
    os.environ["HOME"] = home
    os.environ["USERPROFILE"] = home
    config.add_cleanup(lambda: shutil.rmtree(home, ignore_errors=True))


@pytest.fixture(scope="session")
def geometry_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[RadiotherapyApp]:
    """Provide the one offscreen RadiotherapyApp the geometry and PDF modules need, HOME in a temp folder.

    A fixture, not a test, shared by tests/mesh/ and tests/pdf/. classes.mesh.cylinder reads
    get_app() when it is imported and when it builds a solid, and classes.pdf imports it, so the
    app must exist first. HOME and USERPROFILE are redirected before
    brachify is imported, because classes.info fixes ~/brachify at import time. Qt allows one
    QApplication per process, so an app another fixture already started is reused. An app it
    starts gets window set to None, as RadiotherapyApp.gui() would set it later, so a window
    fixture that saves the previous window does not raise AttributeError when it runs after
    these tests. Fails with an import error if brachify's modules cannot be loaded.
    """
    with pytest.MonkeyPatch.context() as environment:
        home = str(tmp_path_factory.mktemp("geometry-home"))
        environment.setenv("HOME", home)
        environment.setenv("USERPROFILE", home)
        environment.setenv("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        from classes.app import RadiotherapyApp

        app = QApplication.instance()
        if app is None:
            app = RadiotherapyApp(["geometry-tests"])
            app.window = None
        yield app


@pytest.fixture
def default_settings(geometry_app: RadiotherapyApp) -> Iterator[dict[str, float]]:
    """Give each test a fresh copy of the default settings as the app's live settings.

    A fixture, not a test. The geometry reads the live settings, so a test that changes one
    must not leak it into the next test. The previous settings are put back afterwards.
    """
    from settings.defaults import DEFAULT_CONFIG_VALUES

    previous = geometry_app.values.config_values
    geometry_app.values.config_values = DEFAULT_CONFIG_VALUES.copy()
    yield geometry_app.values.config_values
    geometry_app.values.config_values = previous
