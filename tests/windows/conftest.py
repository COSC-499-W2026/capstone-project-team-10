from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from PySide6.QtCore import QCoreApplication

    from windows.main_window import MainWindow


@pytest.fixture(scope="session")
def brachify_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[QCoreApplication]:
    """Start one offscreen RadiotherapyApp for the whole run, with HOME in a temporary folder.

    A fixture, not a test. HOME and USERPROFILE are redirected before brachify is imported,
    because classes.info fixes ~/brachify at import time and Values reads the last config file
    from there. Without this, the tests would load whatever config the developer last opened
    and write app.log into their home folder. Qt allows one QApplication per process, so an
    app another fixture already started (such as a channels fixture in tests/views/) is reused
    rather than created twice, which would raise RuntimeError. Fails with an import error if
    brachify's modules cannot be loaded.
    """
    home = tmp_path_factory.mktemp("home")
    with pytest.MonkeyPatch.context() as environment:
        environment.setenv("HOME", str(home))
        environment.setenv("USERPROFILE", str(home))
        environment.setenv("QT_QPA_PLATFORM", "offscreen")

        from PySide6.QtWidgets import QApplication

        from classes.app import RadiotherapyApp

        yield QApplication.instance() or RadiotherapyApp(["brachify-tests"])


@pytest.fixture
def fresh_window(brachify_app: QCoreApplication) -> Iterator[MainWindow]:
    """Build brachify's real main window, models and five views, with no plan and no cylinder.

    A fixture, not a test. It does what RadiotherapyApp.gui() and MainWindow.initViews() do,
    except that the 3D canvas is created but never initialised and the window is never shown,
    because OpenCASCADE's viewer segfaults (exit 139) without a display. Each test gets a new
    window, since importing a plan or applying settings cannot be undone. The app's signals
    outlive every window, so afterwards this window's navigation and models are disconnected
    from them. Otherwise the next test's tab clicks and height changes would also drive this
    old window. Fails with an exception from MainWindow or a view if the window cannot be
    assembled.
    """
    # These must come after the app exists. BrachyCylinder.__init__ calls get_app() in a
    # default argument, which runs when classes.mesh.cylinder is imported.
    from classes.app import get_app
    from windows.main_window import MainWindow
    from windows.models.navigation_model import NavigationModel
    from windows.views.viewport import OrbitCameraViewer3d

    app = get_app()
    app.window = MainWindow()
    app.window.initModels()
    app.window.canvas = OrbitCameraViewer3d()
    app.window.navigationmodel = NavigationModel()
    window = app.window
    yield window

    app.signals.viewChanged.disconnect(window.navigationmodel.set_page)
    app.signals.height_changed.disconnect(window.channelsmodel.update_height_offset)
    app.signals.height_changed.disconnect(window.tandemmodel.update_height_offset)
