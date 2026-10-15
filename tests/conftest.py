from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from classes.app import RadiotherapyApp


@pytest.fixture(scope="session")
def geometry_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[RadiotherapyApp]:
    """Provide the one offscreen RadiotherapyApp the geometry and PDF modules need, HOME in a temp folder.

    A fixture, not a test, shared by tests/mesh/ and tests/pdf/. classes.mesh.cylinder reads
    get_app() when it is imported and when it builds a solid, and classes.pdf imports it, so the
    app must exist first. HOME and USERPROFILE are redirected before
    brachify is imported, because classes.info fixes ~/brachify at import time. Qt allows one
    QApplication per process, so an app another fixture already started is reused. Fails with
    an import error if brachify's modules cannot be loaded.
    """
    with pytest.MonkeyPatch.context() as environment:
        home = str(tmp_path_factory.mktemp("geometry-home"))
        environment.setenv("HOME", home)
        environment.setenv("USERPROFILE", home)
        environment.setenv("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        from classes.app import RadiotherapyApp

        yield QApplication.instance() or RadiotherapyApp(["geometry-tests"])


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
