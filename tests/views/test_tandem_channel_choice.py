"""Exercise the Tandem tab's Tandem Channel choice, against Ex2, whose channel 14 is named Tandem."""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from windows.main_window import MainWindow
    from windows.views.tandem_view import TandemView

TANDEM_TAB = 3
PLAN_TANDEM = "Tandem"
OFF_AXIS_NEEDLE = "Applicator7"
MOVED_NEEDLE = "Applicator3"


class StubbedRotationAnswer:
    """Stand in for the rotation warning dialog, as a helper and not a test.

    Assigned to TandemView.confirm_rotation, the view's seam for its dialog, so no module is
    patched. It counts the questions asked and gives the chosen answer, True meaning Yes.
    """

    def __init__(self, answer: bool) -> None:
        """Remember the answer to give. A helper, not a test."""
        self.answer = answer
        self.asked = 0

    def __call__(self) -> bool:
        """Record that the view asked, and answer. A helper, not a test."""
        self.asked += 1
        return self.answer


@pytest.fixture
def tandem_tab(tandem_window: MainWindow) -> Iterator[TandemView]:
    """Give a test the Tandem tab of the Ex2 window, and put the plan's own tandem back after.

    A fixture, not a test. The window is shared by the module, so each test starts with
    channel 14, Tandem, as the tandem channel, the way Ex2 imports, and with the rotation
    warning not yet shown.
    """
    view = tandem_window.navigationmodel.views[TANDEM_TAB]
    view.hasShownRotationWarning = False
    yield view
    tandem_window.channelsmodel.set_tandem(PLAN_TANDEM)
    view.refresh_tandem_channels()


def choose(view: TandemView, label: str | None) -> None:
    """Pick a channel in the Tandem Channel box the way a clinician does, None meaning None.

    A helper, not a test. It sets the row and emits activated, the signal a click on an item
    emits, because the box is never shown offscreen and so cannot be clicked.
    """
    box = view.ui.cb_tandem_channel
    index = box.findData(label) if label else 0
    box.setCurrentIndex(index)
    box.activated.emit(index)


def test_the_choice_lists_none_then_every_channel_and_shows_the_plans_tandem(tandem_tab: TandemView) -> None:
    """Check the box lists None first, then each of Ex2's 13 channels with its number, Tandem selected.

    Fails if None is missing, a channel is missing, a row lacks the channel number, or the box
    does not show channel 14 after import. The number is what the reference sheet prints beside
    the T, so it is how the clinician matches the choice to the afterloader channel.
    """
    box = tandem_tab.ui.cb_tandem_channel

    assert box.count() == 14
    assert box.itemText(0) == "None"
    assert box.itemText(13) == "Tandem (14)"
    assert box.currentText() == "Tandem (14)"


def test_choosing_a_channel_makes_it_the_tandem_and_aims_the_tandem_at_it(
    tandem_window: MainWindow, tandem_tab: TandemView,
) -> None:
    """Check choosing Applicator7 makes it the tandem channel, re-enables Tandem and aims the tandem.

    The rotation dialog is answered Yes. Fails if the plan still names Tandem, if Applicator7 is
    not the only channel left out of the cut, if the tandem is not turned to Applicator7's
    64.929 degrees, or the Rotation boxes do not show it. This is what Set as Tandem on the
    Channels tab did, so the Tandem tab must do exactly the same.
    """
    tandem_tab.confirm_rotation = StubbedRotationAnswer(True)

    choose(tandem_tab, OFF_AXIS_NEEDLE)

    assert tandem_window.dicommodel.data.tandem_channel == OFF_AXIS_NEEDLE
    assert tandem_window.channelsmodel.disabled_channels == [OFF_AXIS_NEEDLE]
    assert tandem_window.tandemmodel.rotation == pytest.approx(64.929, abs=0.001)
    assert tandem_tab.ui.tandem_rotation_2.value() == pytest.approx(64.929, abs=0.001)


def test_answering_no_to_the_rotation_warning_keeps_the_plans_tandem(
    tandem_window: MainWindow, tandem_tab: TandemView,
) -> None:
    """Check No in the rotation dialog leaves Tandem as the tandem channel and the box showing it.

    Fails if the dialog is not asked, if Applicator7 stays the tandem, or the box keeps showing
    Applicator7. No means the clinician wants the plan's rotation, and a box that disagreed with
    the model would show a tandem channel that is not the one cut.
    """
    answer = tandem_tab.confirm_rotation = StubbedRotationAnswer(False)

    choose(tandem_tab, OFF_AXIS_NEEDLE)

    assert answer.asked == 1
    assert tandem_window.dicommodel.data.tandem_channel == PLAN_TANDEM
    assert tandem_tab.ui.cb_tandem_channel.currentText() == "Tandem (14)"


def test_choosing_none_clears_the_tandem_channel(tandem_window: MainWindow, tandem_tab: TandemView) -> None:
    """Check choosing None leaves no tandem channel and puts channel 14 back as a needle.

    Fails if the plan still names a tandem channel or any channel stays left out of the cut.
    This is the clear the Channels tab's Clear Tandem button never did (section 7.8 of the
    project docs).
    """
    choose(tandem_tab, None)

    assert tandem_window.dicommodel.data.tandem_channel is None
    assert tandem_window.channelsmodel.disabled_channels == []


def test_an_off_axis_channel_is_warned_about_and_the_plans_tandem_is_not(tandem_tab: TandemView) -> None:
    """Check choosing Applicator7 shows how far off the axis it is, and choosing Tandem hides it.

    Applicator7 crosses the base at (3.29, 6.425), 7.2 mm from the axis, worked by hand, and
    Tandem at (1.14, 0.448), 1.2 mm, inside the 1.9 mm tandem radius. Fails if the warning is
    hidden for Applicator7, does not give 7.2 mm, has a colon or an em dash, or still shows for
    Tandem. The tandem hole is always cut on the axis, so a needle chosen as the tandem gets no
    hole of its own, and the clinician must be told before printing.
    """
    tandem_tab.confirm_rotation = StubbedRotationAnswer(True)
    warning = tandem_tab.ui.label_tandem_channel_warning

    choose(tandem_tab, OFF_AXIS_NEEDLE)
    text = warning.text()
    assert not warning.isHidden()
    assert "Applicator7" in text and "7.2 mm" in text
    assert ":" not in text and "—" not in text

    choose(tandem_tab, PLAN_TANDEM)
    assert warning.isHidden()


def test_a_moved_channel_is_refused_and_the_reason_shown(tandem_window: MainWindow, tandem_tab: TandemView) -> None:
    """Check a moved channel cannot be chosen, the box goes back to Tandem and says why.

    Fails if Applicator3 becomes the tandem, the box keeps showing it, or the warning does not
    tell the clinician to reset the move. The tandem is aimed from the plan path, so a moved
    channel's move could no longer be seen or undone once it was the tandem.
    """
    tandem_window.channelsmodel.move_channel(MOVED_NEEDLE, 10.0, 0.0, 0.0)
    try:
        choose(tandem_tab, MOVED_NEEDLE)

        assert tandem_window.dicommodel.data.tandem_channel == PLAN_TANDEM
        assert tandem_tab.ui.cb_tandem_channel.currentText() == "Tandem (14)"
        assert "Reset" in tandem_tab.ui.label_tandem_channel_warning.text()
    finally:
        tandem_window.channelsmodel.move_channel(MOVED_NEEDLE, 0.0, 0.0, 0.0)


def test_the_box_follows_a_tandem_set_from_the_channels_tab(tandem_window: MainWindow, tandem_tab: TandemView) -> None:
    """Check the box shows a tandem channel set anywhere else, such as the Channels tab's button.

    Fails if the box still shows Tandem after Applicator9 is made the tandem through the model.
    Two controls that disagree would leave the clinician unsure which channel is the tandem.
    """
    tandem_window.channelsmodel.set_tandem("Applicator9")

    assert tandem_tab.ui.cb_tandem_channel.currentText() == "Applicator9 (9)"


def test_generate_spin_boxes_keep_their_height_in_the_default_window(
    tandem_window: MainWindow, tandem_tab: TandemView,
) -> None:
    """Check the Generate sub-tab's spin boxes stay at least 20 px tall in brachify's default window.

    tandem_window is 770 by 472, the size main_window.ui opens at, and the Tandem tab is opened
    on Generate. Fails if any spin box is shorter than 20 px, the least that still shows its
    value. The Tandem Channel row made the tab taller than the space under the six nav
    buttons, and Qt squeezed the boxes to 14 px, so the clinician could not read the tandem's
    height, diameters, angle or rotation.
    """
    from classes.app import get_app

    get_app().signals.viewChanged.emit(TANDEM_TAB)
    ui = tandem_tab.ui
    ui.ab.setCurrentWidget(ui.Generate)
    tandem_tab.grab()

    for spin_box in (ui.sb_tandem_height, ui.sp_channel_diameter, ui.sp_stopper_diameter, ui.sp_bend_angle,
                     ui.sb_bend_radius, ui.sb_threading_depth, ui.sb_threading_diameter, ui.tandem_rotation_2):
        spin_box.grab()
        assert spin_box.height() >= 20, spin_box.objectName()


def test_the_tandem_tab_never_scrolls_sideways_in_the_default_window(
    tandem_window: MainWindow, tandem_tab: TandemView,
) -> None:
    """Check the Tandem tab's scroll area scrolls up and down only, at 770 by 472.

    Fails if the scroll area is missing or the rows are wider than the panel. A sideways scroll
    bar would cut off the right edge, where the spin box arrows and the Tandem Channel box sit.
    """
    from PySide6.QtWidgets import QScrollArea

    from classes.app import get_app

    get_app().signals.viewChanged.emit(TANDEM_TAB)
    scroll = tandem_tab.findChild(QScrollArea, "scroll_tandem")
    tandem_window.grab()

    assert scroll.horizontalScrollBar().maximum() == 0
