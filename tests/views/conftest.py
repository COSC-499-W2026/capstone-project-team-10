from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from classes.app import RadiotherapyApp
    from windows.main_window import MainWindow


@pytest.fixture(scope="session")
def units_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[RadiotherapyApp]:
    """Provide one real offscreen app with its user files in a temporary home.

    This fixture fails on an import or Qt startup error. Isolating the filesystem prevents
    a developer's saved configuration from changing the tests or being overwritten.
    """
    with pytest.MonkeyPatch.context() as environment:
        temporary_home = str(tmp_path_factory.mktemp("units-home"))
        environment.setenv("HOME", temporary_home)
        environment.setenv("USERPROFILE", temporary_home)
        environment.setenv("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication
        from classes.app import RadiotherapyApp

        yield QApplication.instance() or RadiotherapyApp(["units-tests"])


@pytest.fixture
def cylinder_window(units_app: RadiotherapyApp) -> Iterator[MainWindow]:
    """Assemble the real window and views without starting the native viewport.

    This fixture fails if the real models or views cannot be built. Each test gets fresh
    settings and disconnected signals afterwards, preventing edits leaking between tests.
    """
    from settings.defaults import DEFAULT_CONFIG_VALUES
    from windows.main_window import MainWindow
    from windows.models.navigation_model import NavigationModel
    from windows.views.viewport import OrbitCameraViewer3d

    previous_config = units_app.values.config_values
    units_app.values.config_values = DEFAULT_CONFIG_VALUES.copy()
    units_app.window = MainWindow()
    units_app.window.initModels()
    units_app.window.canvas = OrbitCameraViewer3d()
    units_app.window.navigationmodel = NavigationModel()
    window = units_app.window
    yield window
    units_app.signals.viewChanged.disconnect(window.navigationmodel.set_page)
    units_app.signals.height_changed.disconnect(window.channelsmodel.update_height_offset)
    units_app.signals.height_changed.disconnect(window.tandemmodel.update_height_offset)
    units_app.values.config_values = previous_config
