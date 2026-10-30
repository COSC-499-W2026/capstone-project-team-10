"""Exercise the Export tab's warning for a tandem channel with no tandem hole, against Ex2."""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from windows.main_window import MainWindow
    from windows.views.export_view import Export_View

CYLINDER_TAB = 1
EXPORT_TAB = 4
PLAN_TANDEM = "Tandem"


class StubbedExportAnswer:
    """Stand in for the export confirmation dialog, as a helper and not a test.

    Assigned to Export_View.confirm_export, the view's seam for its dialog, so no module is
    patched. It records the text it was asked with and gives the chosen answer, True meaning Yes.
    """

    def __init__(self, answer: bool) -> None:
        """Remember the answer to give. A helper, not a test."""
        self.answer = answer
        self.asked: list[str] = []

    def __call__(self, text: str) -> bool:
        """Record the question and answer it. A helper, not a test."""
        self.asked.append(text)
        return self.answer


@pytest.fixture
def export_tab(tandem_window: MainWindow) -> Iterator[Export_View]:
    """Give a test the Ex2 window's Export tab, as imported, with no tandem hole yet.

    A fixture, not a test. Afterwards the plan's own tandem channel is set again, any tandem is
    cleared and the Cylinder tab is shown, so each test opens the Export tab fresh.
    """
    yield tandem_window.navigationmodel.views[EXPORT_TAB]
    tandem_window.channelsmodel.set_tandem(PLAN_TANDEM)
    tandem_window.tandemmodel.clear_tandem()
    open_tab(tandem_window, CYLINDER_TAB)


def open_tab(window: MainWindow, index: int) -> None:
    """Show one tab through the app's navigation signal, as a nav button click does. A helper, not a test."""
    from classes.app import get_app

    get_app().signals.viewChanged.emit(index)


def generate_tandem(window: MainWindow) -> None:
    """Generate a tandem at 150 mm, which a 160 mm cylinder can hold. A helper, not a test."""
    window.tandemmodel.tandem_length = 150.0
    window.tandemmodel.set_tandem()


def test_the_export_tab_warns_that_the_tandem_channel_has_no_hole(
    tandem_window: MainWindow, export_tab: Export_View,
) -> None:
    """Check that Ex2, imported and never given a tandem, opens the Export tab with a warning.

    Fails if the warning is hidden, does not name the Tandem channel, or has a colon or an em
    dash. Right after import Ex2's channel 14 is left out of the cut, and with no tandem
    generated or imported the printed cylinder has no hole for the tandem the plan uses.
    """
    open_tab(tandem_window, EXPORT_TAB)
    warning = export_tab.ui.label_tandem_hole_warning

    assert not warning.isHidden()
    assert "Tandem" in warning.text() and "no tandem hole" in warning.text()
    assert ":" not in warning.text() and "—" not in warning.text()


def test_no_warning_once_a_tandem_is_generated(tandem_window: MainWindow, export_tab: Export_View) -> None:
    """Check the warning is hidden when the tandem channel has a generated tandem hole.

    Fails if it still shows. A warning on every correct export teaches the clinician to ignore it.
    """
    generate_tandem(tandem_window)
    open_tab(tandem_window, EXPORT_TAB)

    assert export_tab.ui.label_tandem_hole_warning.isHidden()


def test_no_warning_without_a_tandem_channel(tandem_window: MainWindow, export_tab: Export_View) -> None:
    """Check the warning is hidden when no channel is the tandem channel, a needles-only cylinder.

    Fails if it shows. A cylinder with no tandem channel and no tandem hole is a correct device.
    """
    tandem_window.channelsmodel.set_tandem(None)
    open_tab(tandem_window, EXPORT_TAB)

    assert export_tab.ui.label_tandem_hole_warning.isHidden()


def test_exporting_asks_first_and_no_stops_it(tandem_window: MainWindow, export_tab: Export_View) -> None:
    """Check exporting with the warning showing asks once, with the warning, and No stops the export.

    Fails if the clinician is not asked, is asked with other text, or the export goes ahead after
    No. The warning line alone can be missed, and the exported file is what gets printed.
    """
    answer = export_tab.confirm_export = StubbedExportAnswer(False)
    open_tab(tandem_window, EXPORT_TAB)

    allowed = export_tab.export_allowed()

    assert not allowed
    assert answer.asked == [export_tab.ui.label_tandem_hole_warning.text()]


def test_exporting_with_a_tandem_hole_asks_nothing(tandem_window: MainWindow, export_tab: Export_View) -> None:
    """Check exporting a cylinder whose tandem channel has a hole goes ahead without a question.

    Fails if the clinician is asked or the export is stopped, which would get in the way of every
    correct export.
    """
    answer = export_tab.confirm_export = StubbedExportAnswer(False)
    generate_tandem(tandem_window)
    open_tab(tandem_window, EXPORT_TAB)

    assert export_tab.export_allowed()
    assert answer.asked == []
