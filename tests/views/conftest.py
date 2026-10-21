from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from classes.app import RadiotherapyApp
    from windows.main_window import MainWindow

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PLAN = REPO_ROOT / "SI_C_D30 Brachify_Ex1"


@pytest.fixture(scope="session")
def units_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[RadiotherapyApp]:
    """Provide one real offscreen app with its user files in a temporary home.

    This fixture fails on an import or Qt startup error. Isolating the filesystem prevents
    a developer's saved configuration from changing the tests or being overwritten.
    Both channels_window and cylinder_window build on it, because Qt allows one
    QApplication per process, so a second fixture constructing its own would fail with a
    RuntimeError in whichever test file runs second.
    """
    with pytest.MonkeyPatch.context() as environment:
        temporary_home = str(tmp_path_factory.mktemp("units-home"))
        environment.setenv("HOME", temporary_home)
        environment.setenv("USERPROFILE", temporary_home)
        environment.setenv("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication
        from classes.app import RadiotherapyApp

        app = QApplication.instance()
        if app is None:
            app = RadiotherapyApp(["units-tests"])
            app.window = None
        yield app


@pytest.fixture(scope="module")
def channels_window(units_app: RadiotherapyApp) -> Iterator[MainWindow]:
    """Build brachify's real main window, models and five views, with the Ex1 plan imported.

    A fixture, not a test. It does what RadiotherapyApp.gui() and MainWindow.initViews() do,
    except that the 3D canvas is created but never initialised and the window is never shown.
    OpenCASCADE's viewer segfaults (exit 139) without a display, so initialising it would
    kill the test run. The plan is imported the way ImportView.action_import_dicom_folder
    does it, minus the folder dialog: read_dicom_folder, DicomModel.update, then
    ChannelsView.create_channels_list.

    units_app points HOME and USERPROFILE at a temporary folder before brachify is imported,
    because classes.info fixes ~/brachify at import time and Values reads the last config
    file from there. Without this, the tests would load whatever config the developer last
    opened and write app.log into their home folder. The module scope exists because
    building the thirteen Ex1 channels takes several seconds. Teardown disconnects the
    window from the application signals, so a later test module's height change or page
    switch does not also drive this window. Fails with an import error, or an exception
    from the DICOM readers, if the app cannot be assembled or the sample plan no longer loads.
    """
    # These must come after the app exists. BrachyCylinder.__init__ calls get_app() in a
    # default argument, which runs when classes.mesh.cylinder is imported.
    from classes.dicom.fileio import read_dicom_folder
    from windows.main_window import MainWindow
    from windows.models.navigation_model import NavigationModel
    from windows.views.viewport import OrbitCameraViewer3d

    units_app.window = MainWindow()
    units_app.window.initModels()
    units_app.window.canvas = OrbitCameraViewer3d()
    units_app.window.navigationmodel = NavigationModel()
    window = units_app.window

    window.dicommodel.update(read_dicom_folder(str(SAMPLE_PLAN)))
    window.navigationmodel.views[2].create_channels_list()
    yield window
    units_app.signals.viewChanged.disconnect(window.navigationmodel.set_page)
    units_app.signals.height_changed.disconnect(window.channelsmodel.update_height_offset)
    units_app.signals.height_changed.disconnect(window.tandemmodel.update_height_offset)


@pytest.fixture
def cylinder_window(units_app: RadiotherapyApp) -> Iterator[MainWindow]:
    """Assemble the real window and views without starting the native viewport.

    This fixture fails if the real models or views cannot be built. Each test gets fresh
    settings and disconnected signals afterwards, preventing edits leaking between tests.
    Restoring the previous app window keeps later shared-window tests on their own models.
    """
    from settings.defaults import DEFAULT_CONFIG_VALUES
    from windows.main_window import MainWindow
    from windows.models.navigation_model import NavigationModel
    from windows.views.viewport import OrbitCameraViewer3d

    previous_config = units_app.values.config_values
    previous_window = units_app.window
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
    units_app.window = previous_window
