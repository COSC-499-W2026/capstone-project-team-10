from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from windows.main_window import MainWindow

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PLAN = REPO_ROOT / "SI_C_D30 Brachify_Ex1"


@pytest.fixture(scope="session")
def channels_window(tmp_path_factory: pytest.TempPathFactory) -> Iterator[MainWindow]:
    """Build brachify's real main window, models and five views, with the Ex1 plan imported.

    A fixture, not a test. It does what RadiotherapyApp.gui() and MainWindow.initViews() do,
    except that the 3D canvas is created but never initialised and the window is never shown.
    OpenCASCADE's viewer segfaults (exit 139) without a display, so initialising it would
    kill the test run. The plan is imported the way ImportView.action_import_dicom_folder
    does it, minus the folder dialog: read_dicom_folder, DicomModel.update, then
    ChannelsView.create_channels_list.

    HOME and USERPROFILE point at a temporary folder before brachify is imported, because
    classes.info fixes ~/brachify at import time and Values reads the last config file from
    there. Without this, the tests would load whatever config the developer last opened and
    write app.log into their home folder. The session scope exists because Qt allows one
    QApplication per process and building the thirteen Ex1 channels takes several seconds.
    Fails with an import error, or an exception from the DICOM readers, if the app cannot be
    assembled or the sample plan no longer loads.
    """
    home = tmp_path_factory.mktemp("home")
    with pytest.MonkeyPatch.context() as environment:
        environment.setenv("HOME", str(home))
        environment.setenv("USERPROFILE", str(home))
        environment.setenv("QT_QPA_PLATFORM", "offscreen")

        from classes.app import RadiotherapyApp

        app = RadiotherapyApp(["brachify-tests"])

        # These must come after the app exists. BrachyCylinder.__init__ calls get_app() in a
        # default argument, which runs when classes.mesh.cylinder is imported.
        from classes.dicom.fileio import read_dicom_folder
        from windows.main_window import MainWindow
        from windows.models.navigation_model import NavigationModel
        from windows.views.viewport import OrbitCameraViewer3d

        app.window = MainWindow()
        app.window.initModels()
        app.window.canvas = OrbitCameraViewer3d()
        app.window.navigationmodel = NavigationModel()

        app.window.dicommodel.update(read_dicom_folder(str(SAMPLE_PLAN)))
        app.window.navigationmodel.views[2].create_channels_list()
        yield app.window
