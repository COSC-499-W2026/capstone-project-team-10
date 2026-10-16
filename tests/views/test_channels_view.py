from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDoubleSpinBox, QListWidgetItem, QPushButton, QStyle

    from windows.main_window import MainWindow

CYLINDER_TAB = 1
CHANNELS_TAB = 2
FIRST_CHANNEL = "Applicator2"
SECOND_CHANNEL = "Applicator3"


def select_first_channel_then_leave_and_return(window: MainWindow) -> None:
    """Open the Channels tab, pick its first channel, go to the Cylinder tab and come back.

    A helper, not a test. It is the user's sequence from the bug report, driven through the
    real navigation signal. setCurrentRow emits currentItemChanged, the same signal a mouse
    click on the list emits, so the view and model react exactly as they do to a click.
    """
    # Imported here, not at the top: importing classes at collection time would fix
    # ~/brachify to the real home folder before the units_app fixture redirects HOME.
    from classes.app import get_app

    signals = get_app().signals
    signals.viewChanged.emit(CHANNELS_TAB)
    window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels.setCurrentRow(0)
    signals.viewChanged.emit(CYLINDER_TAB)
    signals.viewChanged.emit(CHANNELS_TAB)


def test_returning_to_channels_tab_shows_no_channel_selected(channels_window: MainWindow) -> None:
    """Check the channel list highlights nothing after leaving the Channels tab and coming back.

    Leaving the tab clears the model's selection, so no channel is drawn in the selected
    colour. The list must agree. Fails if Applicator2 is still the list's current or
    selected item, which is the reported bug: the list showed a channel highlighted in blue
    while the viewport showed it unselected, so the clinician could not tell which channel
    Disable or Set as Tandem would act on.
    """
    select_first_channel_then_leave_and_return(channels_window)
    channel_list = channels_window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels

    assert channel_list.selectedItems() == []
    assert channel_list.currentItem() is None


def test_channel_can_be_selected_again_after_returning_to_channels_tab(
    channels_window: MainWindow,
) -> None:
    """Check that clicking the previously selected channel after coming back selects it.

    Fails if the model's selection is still empty after the click. Qt only emits
    currentItemChanged when the current item changes, so while the list keeps Applicator2
    as its current item, clicking it again does nothing and the clinician cannot select
    that channel until they click a different one first.
    """
    select_first_channel_then_leave_and_return(channels_window)
    channel_list = channels_window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels

    channel_list.setCurrentRow(0)

    assert channels_window.channelsmodel.get_selected_channel() == FIRST_CHANNEL


def darkest_pixel_in_arrow(spin_box: QDoubleSpinBox, arrow: QStyle.SubControl) -> int:
    """Render a spin box and return the lightness, 0 to 255, of the darkest pixel in one arrow.

    A helper, not a test. It asks the spin box's own style where the up or down button is,
    so it measures the button the user clicks, whatever the platform style. It grabs first,
    because the window is never shown and grab() is what lays the spin box out at its real
    size. Measured before that, the button rectangle points at the wrong pixels.
    """
    from PySide6.QtWidgets import QStyle, QStyleOptionSpinBox

    image = spin_box.grab().toImage()
    option = QStyleOptionSpinBox()
    spin_box.initStyleOption(option)
    button = spin_box.style().subControlRect(
        QStyle.ComplexControl.CC_SpinBox, option, arrow, spin_box)
    return min(
        image.pixelColor(x, y).lightness()
        for x in range(button.left(), button.right() + 1)
        for y in range(button.top(), button.bottom() + 1)
    )


def test_channels_spin_box_arrows_are_black(channels_window: MainWindow) -> None:
    """Check that both arrows of every spin box on the Channels tab are drawn black.

    Fails if an arrow's darkest pixel is lighter than 40, as with the native arrows. macOS
    in dark mode draws them white on the white field the .ui stylesheets paint, so they
    vanish, and the headless Fusion style draws them grey (94). The clinician then cannot see
    the controls that step channel diameter, dead space and threading.
    """
    from PySide6.QtWidgets import QStyle

    ui = channels_window.navigationmodel.views[CHANNELS_TAB].ui
    spin_boxes = (ui.spinbox_diameter, ui.sb_needle_length, ui.sb_threading_dept,
                  ui.sb_threading_diameter, ui.sb_channel_diameter)

    arrows = (("up", QStyle.SubControl.SC_SpinBoxUp), ("down", QStyle.SubControl.SC_SpinBoxDown))

    for spin_box in spin_boxes:
        for name, arrow in arrows:
            assert darkest_pixel_in_arrow(spin_box, arrow) < 40, (spin_box.objectName(), name)


def test_list_click_selects_channel_again_after_picking_another_in_viewport(
    channels_window: MainWindow,
) -> None:
    """Check that clicking a channel in the list selects it after another was picked in 3D.

    The user clicks Applicator2 in the list, picks Applicator3 in the viewport, then clicks
    Applicator2 in the list again. The pick arrives through the canvas's real
    sig_topods_selected signal, carrying the same cached needle shape the viewport displays.
    Fails if the model still holds Applicator3 after the second click. That happens when the
    list keeps Applicator2 as its current item through the viewport pick, so Qt emits no
    currentItemChanged for the second click. Disable and Set as Tandem act on the model's
    channel, so the clinician would disable or make a tandem of a channel other than the
    one highlighted, and that wrong channel is cut into the printed cylinder.
    """
    from classes.app import get_app

    signals = get_app().signals
    signals.viewChanged.emit(CYLINDER_TAB)
    signals.viewChanged.emit(CHANNELS_TAB)
    channel_list = channels_window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels
    picked_needle = channels_window.channelsmodel.channels[SECOND_CHANNEL].shape()

    channel_list.setCurrentRow(0)
    channels_window.canvas.sig_topods_selected.emit([picked_needle])
    channel_list.setCurrentRow(0)

    assert channels_window.channelsmodel.get_selected_channel() == FIRST_CHANNEL


def test_viewport_pick_highlights_only_that_channel_in_list(channels_window: MainWindow) -> None:
    """Check that picking a channel in the viewport makes it the list's highlighted channel.

    The user clicks Applicator2 in the list, then picks Applicator3 in the viewport through
    the canvas's real sig_topods_selected signal. Fails if the list's current item is not
    Applicator3, or if any channel other than Applicator3 is highlighted. The list is the
    only place that names the channel Disable and Set as Tandem will act on, so a list that
    shows no channel, or the previous one, after a pick hides which channel the clinician
    is about to change.
    """
    from classes.app import get_app

    signals = get_app().signals
    signals.viewChanged.emit(CYLINDER_TAB)
    signals.viewChanged.emit(CHANNELS_TAB)
    channel_list = channels_window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels
    picked_needle = channels_window.channelsmodel.channels[SECOND_CHANNEL].shape()

    channel_list.setCurrentRow(0)
    channels_window.canvas.sig_topods_selected.emit([picked_needle])

    assert channel_list.currentItem().text() == SECOND_CHANNEL
    assert [item.text() for item in channel_list.selectedItems()] == [SECOND_CHANNEL]


CARRIED_OVER_CHANNEL = "Applicator7"


def test_loading_a_plan_enables_every_channel_again(channels_window: MainWindow) -> None:
    """Check that a channel disabled in one plan is enabled in the next plan loaded.

    Applicator7 is disabled, then a plan is loaded through ChannelsModel.load_data, the slot
    DicomModel.values_changed calls on every import. Fails if Applicator7 is still disabled, or
    is missing from get_visible_channels, the list the Export cut and the PDF both use. Channel
    labels repeat between plans, so a needle switched off for one patient would otherwise have
    no hole in the next patient's printed cylinder, and nothing on screen says so.
    """
    model = channels_window.channelsmodel
    model.toggle_channel_enabled(CARRIED_OVER_CHANNEL)

    model.load_data(channels_window.dicommodel.data)

    assert not model.is_channel_disabled(CARRIED_OVER_CHANNEL)
    assert CARRIED_OVER_CHANNEL in [channel.label for channel in model.get_visible_channels()]


OWN_DIAMETER_CHANNEL = "Applicator4"
CLEARED_CHANNEL = "Applicator5"
REJECTED_CHANNEL = "Applicator11"
REIMPORTED_CHANNEL = "Applicator12"
GLOBAL_DIAMETER_CHANNEL = "Applicator13"


def test_channel_keeps_its_own_diameter_when_channels_diameter_is_applied(
    channels_window: MainWindow,
) -> None:
    """Check that Apply on the Channels tab leaves a channel's own diameter alone.

    Applicator4 is given 3.2 mm, then the Channels Diameter box is set to 2.5 mm and Apply is
    pressed. Fails if Applicator4 is rebuilt at 2.5 mm, or if Applicator13 is not. That is
    FR-CN-08: a needle that needs a wider channel would silently be printed at the global width
    the next time anyone pressed Apply, and the needle would not fit the printed cylinder. The
    live settings are swapped for a copy and put back afterwards, so the 2.5 mm that Apply
    writes does not leak into later test modules.
    """
    from classes.app import get_app

    values = get_app().values
    live_settings = values.config_values
    values.config_values = live_settings.copy()
    model = channels_window.channelsmodel
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    try:
        model.set_channel_diameter(OWN_DIAMETER_CHANNEL, 3.2)
        view.ui.spinbox_diameter.setValue(2.5)
        view.action_apply_settings()
        assert model.channels[OWN_DIAMETER_CHANNEL].get_diameter() == 3.2
        assert model.channels[GLOBAL_DIAMETER_CHANNEL].get_diameter() == 2.5
    finally:
        values.config_values = live_settings
        model.set_diameter(live_settings["CONFIG_CHANNELS_DIAMETER"])


def test_channel_follows_channels_diameter_again_once_its_own_is_cleared(
    channels_window: MainWindow,
) -> None:
    """Check that clearing a channel's own diameter returns it to the global diameter.

    Fails if Applicator5 keeps 3.4 mm after the clear, or still reports an own diameter. A
    clinician who undoes a per-channel change must get the channel the rest of the plan uses,
    not a leftover width that no control on screen shows.
    """
    model = channels_window.channelsmodel

    model.set_channel_diameter(CLEARED_CHANNEL, 3.4)
    model.clear_channel_diameter(CLEARED_CHANNEL)

    assert model.channels[CLEARED_CHANNEL].get_diameter() == model.channels[GLOBAL_DIAMETER_CHANNEL].get_diameter()
    assert not model.has_own_diameter(CLEARED_CHANNEL)


@pytest.mark.parametrize("diameter", [0.2, float("nan")])
def test_own_diameter_below_the_minimum_or_not_a_number_is_rejected(
    channels_window: MainWindow, diameter: float,
) -> None:
    """Check that a channel cannot be given a diameter below 0.3 mm, or NaN.

    Runs for 0.2 mm and for NaN. Fails if set_channel_diameter does not raise ValueError, or if
    Applicator11 is left with an own diameter or a different width. The global Channels Diameter
    box stops at 0.3 mm, a narrower channel prints as a hole no needle passes through, and NaN
    passes a plain "less than" check, so it would reach the geometry unnoticed.
    """
    model = channels_window.channelsmodel
    before = model.channels[REJECTED_CHANNEL].get_diameter()

    with pytest.raises(ValueError):
        model.set_channel_diameter(REJECTED_CHANNEL, diameter)

    assert not model.has_own_diameter(REJECTED_CHANNEL)
    assert model.channels[REJECTED_CHANNEL].get_diameter() == before


def test_loading_a_plan_clears_every_own_diameter(channels_window: MainWindow) -> None:
    """Check that loading a plan forgets the previous plan's own diameters.

    The plan is loaded through ChannelsModel.load_data, the slot DicomModel.values_changed
    calls on every import. Fails if Applicator12 still reports an own diameter, or is not
    rebuilt at the Channels Diameter in the live settings. Channel labels repeat between plans,
    so a width chosen for one patient's Applicator12 would otherwise be printed into the next
    patient's cylinder.
    """
    from classes.app import get_app

    model = channels_window.channelsmodel

    model.set_channel_diameter(REIMPORTED_CHANNEL, 3.6)
    model.load_data(channels_window.dicommodel.data)

    assert not model.has_own_diameter(REIMPORTED_CHANNEL)
    assert model.channels[REIMPORTED_CHANNEL].get_diameter() == get_app().values.config_values["CONFIG_CHANNELS_DIAMETER"]


def test_clearing_own_diameter_after_config_import_matches_new_channels(
    cylinder_window: MainWindow, tmp_path: Path,
) -> None:
    """Clear to the width used by new channels after loading a different config.

    A real config file sets 3 mm before Ex1 is imported. Clearing a 4 mm override must
    return to 3 mm, like an untouched channel. Returning the startup 2.7 mm fails the
    literal assertion and would cut a narrower hole than the clinician requested.
    """
    from classes.app import get_app
    from classes.dicom.fileio import read_dicom_folder
    from settings.load import load_config_file
    from settings.reset import resetAllValues

    values = get_app().values
    config_file = tmp_path / "channels.json"
    config_file.write_text('{"CONFIG_CHANNELS_DIAMETER": 3.0}')
    values.config_values, _, _ = load_config_file(str(config_file), values.config_values, 0)
    resetAllValues(values.config_values)
    plan = Path(__file__).resolve().parents[2] / "SI_C_D30 Brachify_Ex1"
    cylinder_window.dicommodel.update(read_dicom_folder(str(plan)))
    model = cylinder_window.channelsmodel
    model.set_channel_diameter(OWN_DIAMETER_CHANNEL, 4.0)

    model.clear_channel_diameter(OWN_DIAMETER_CHANNEL)

    assert model.channels[OWN_DIAMETER_CHANNEL].get_diameter() == 3.0
    assert model.channels[GLOBAL_DIAMETER_CHANNEL].get_diameter() == 3.0
    assert not model.has_own_diameter(OWN_DIAMETER_CHANNEL)


@pytest.mark.parametrize("label", ["Missing channel", None])
def test_unknown_channel_cannot_leave_an_own_diameter(
    channels_window: MainWindow, label: str | None,
) -> None:
    """Reject an unknown or unselected channel before storing any diameter.

    A missing label must raise KeyError and leave the override map unchanged. Writing
    the map before looking up the channel fails the assertion and leaves phantom state
    that could later apply to a different channel with that label.
    """
    model = channels_window.channelsmodel
    before = model.own_diameters.copy()

    with pytest.raises(KeyError):
        model.set_channel_diameter(label, 3.0)

    assert model.own_diameters == before

APPLIED_CHANNEL = "Applicator6"
RESET_CHANNEL = "Applicator8"
SHOWN_CHANNEL = "Applicator9"
OTHER_SHOWN_CHANNEL = "Applicator10"


def click(button: QPushButton) -> None:
    """Click a button with the left mouse button, the way a clinician does.

    A helper, not a test. QTest sends a real press and release, so the pressed signal and
    every slot connected to it run. A disabled button ignores the click, so a test that clicks
    a control the view left disabled fails on its assertions.
    """
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)


def select_channel(window: MainWindow, label: str) -> None:
    """Make one channel the Channels list's current row, as clicking it would.

    A helper, not a test. setCurrentRow emits currentItemChanged, the signal a mouse click
    emits, so the view selects the channel in ChannelsModel. Fails with IndexError if the list
    has no row with that label.
    """
    channel_list = window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels
    channel_list.setCurrentRow(channel_list.row(channel_list.findItems(label, Qt.MatchFlag.MatchExactly)[0]))


def open_channels_tab_and_select(window: MainWindow, label: str) -> None:
    """Open the Channels tab fresh, then select one channel in its list.

    A helper, not a test. Leaving for the Cylinder tab first runs on_close and on_open, as a
    clinician arriving at the tab would, so no earlier selection carries over.
    """
    from classes.app import get_app

    get_app().signals.viewChanged.emit(CYLINDER_TAB)
    get_app().signals.viewChanged.emit(CHANNELS_TAB)
    select_channel(window, label)


def test_apply_to_channel_changes_only_the_selected_channel(channels_window: MainWindow) -> None:
    """Check that Apply to Channel gives the selected channel, and only it, the typed diameter.

    Fails if Applicator6 is not rebuilt at 3.3 mm, or if Applicator13's diameter changes. A
    clinician widening one needle's channel must not resize every other channel in the
    cylinder. Applicator13 is compared with its own value from before the click, not with the
    global diameter, because an earlier test in this module reloads the plan.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    untouched_before = model.channels[GLOBAL_DIAMETER_CHANNEL].get_diameter()
    open_channels_tab_and_select(channels_window, APPLIED_CHANNEL)

    view.ui.sb_channel_diameter.setValue(3.3)
    click(view.ui.btn_apply_channel_diameter)

    assert model.channels[APPLIED_CHANNEL].get_diameter() == 3.3
    assert model.channels[GLOBAL_DIAMETER_CHANNEL].get_diameter() == untouched_before


def test_selected_channel_controls_are_disabled_with_no_channel_selected(
    channels_window: MainWindow,
) -> None:
    """Check that the Selected Channel group cannot be used until a channel is selected.

    Arriving at the Channels tab selects nothing. Fails if the group is enabled then. With no
    channel selected, Apply to Channel would have no channel to change, and the clinician could
    not tell which needle the box refers to. This is FR-CN-02's interface test case.
    """
    from classes.app import get_app

    get_app().signals.viewChanged.emit(CYLINDER_TAB)
    get_app().signals.viewChanged.emit(CHANNELS_TAB)

    assert not channels_window.navigationmodel.views[CHANNELS_TAB].ui.group_selected_channel.isEnabled()


def test_use_channels_diameter_returns_the_selected_channel_to_the_global_diameter(
    channels_window: MainWindow,
) -> None:
    """Check that Use Channels Diameter undoes a channel's own diameter, then disables itself.

    Fails if Applicator8 keeps 3.4 mm, still reports an own diameter, or the button stays
    enabled when there is nothing left to undo. This is the clinician's only way back to the
    plan-wide width without re-importing the plan.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    open_channels_tab_and_select(channels_window, RESET_CHANNEL)
    view.ui.sb_channel_diameter.setValue(3.4)
    click(view.ui.btn_apply_channel_diameter)

    click(view.ui.btn_clear_channel_diameter)

    assert model.channels[RESET_CHANNEL].get_diameter() == model.channels[GLOBAL_DIAMETER_CHANNEL].get_diameter()
    assert not model.has_own_diameter(RESET_CHANNEL)
    assert not view.ui.btn_clear_channel_diameter.isEnabled()


def test_channel_diameter_box_stops_at_the_minimum(channels_window: MainWindow) -> None:
    """Check that the Channel Diameter box will not hold less than 0.3 mm.

    Fails if typing 0.1 mm leaves 0.1 in the box. The model rejects anything narrower, and a
    narrower channel prints as a hole no needle passes through, so the box must stop the value
    before Apply to Channel is pressed.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]

    view.ui.sb_channel_diameter.setValue(0.1)

    assert view.ui.sb_channel_diameter.value() == 0.3


def test_selecting_a_channel_shows_its_current_diameter(channels_window: MainWindow) -> None:
    """Check that the Channel Diameter box shows the diameter of whichever channel is selected.

    Applicator9 is given 3.1 mm. Applicator10 is selected, 1.0 is typed into the box and never
    applied, then Applicator9 is selected. Fails if the box did not first show Applicator10's
    diameter, or does not then read 3.1. A box that kept a typed value across selections would
    make the clinician think a channel had a width it does not have.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    model.set_channel_diameter(SHOWN_CHANNEL, 3.1)
    open_channels_tab_and_select(channels_window, OTHER_SHOWN_CHANNEL)
    shown_for_other = view.ui.sb_channel_diameter.value()
    view.ui.sb_channel_diameter.setValue(1.0)

    select_channel(channels_window, SHOWN_CHANNEL)

    assert shown_for_other == model.channels[OTHER_SHOWN_CHANNEL].get_diameter()
    assert view.ui.sb_channel_diameter.value() == 3.1


def test_channels_settings_keep_their_height_in_the_default_window(channels_window: MainWindow) -> None:
    """Check that the Channels spin boxes keep their full height in brachify's default window.

    channels_window is 770 by 472, the size main_window.ui opens at. The Channels tab is opened
    fresh and a channel selected. Fails if any of the four Channels spin boxes is shorter than
    20 px, the least that still shows its value. They are 21 px when the tab fits. Each control
    added under the list makes the tab taller, and once it no longer fits, Qt squeezes the spin
    boxes to 9 px, so the clinician cannot read or set the channel diameter, dead space or
    threading.
    """
    ui = channels_window.navigationmodel.views[CHANNELS_TAB].ui
    open_channels_tab_and_select(channels_window, APPLIED_CHANNEL)

    for spin_box in (ui.spinbox_diameter, ui.sb_needle_length, ui.sb_threading_dept, ui.sb_threading_diameter):
        spin_box.grab()
        assert spin_box.height() >= 20, spin_box.objectName()


MARKED_CHANNEL = "Applicator2"
UNMARKED_AGAIN_CHANNEL = "Applicator3"
DISABLED_CHANNEL = "Applicator7"
TANDEM_CHANNEL = "Applicator12"


def channel_item(window: MainWindow, label: str) -> QListWidgetItem:
    """Return the Channels list row that shows one channel.

    A helper, not a test. Fails with IndexError if the list has no row with that label, which
    would mean the list no longer shows the plan's channels.
    """
    channel_list = window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels
    return channel_list.findItems(label, Qt.MatchFlag.MatchExactly)[0]


def test_channel_with_its_own_diameter_is_bold_on_amber_in_the_list(channels_window: MainWindow) -> None:
    """Check that a channel with its own diameter reads as modified in the Channels list.

    Applicator2 is given 3.0 mm. Fails if its status is not OWN_DIAMETER, if its row is not
    bold, or has the same background as Applicator13, which follows the global diameter, or if
    hovering it does not name the diameter. FR-CN-03 asks that a changed needle shows as
    modified. Without the mark, the clinician cannot see which needles differ from the
    plan-wide width before printing.
    """
    from windows.models.channels_model import ChannelStatus

    channels_window.channelsmodel.set_channel_diameter(MARKED_CHANNEL, 3.0)
    marked = channel_item(channels_window, MARKED_CHANNEL)
    reference = channel_item(channels_window, GLOBAL_DIAMETER_CHANNEL)

    assert channels_window.channelsmodel.channel_status(MARKED_CHANNEL) is ChannelStatus.OWN_DIAMETER
    assert marked.font().bold() and not marked.font().italic()
    assert not reference.font().bold()
    assert marked.background() != reference.background()
    assert marked.toolTip() == "Own diameter 3.000 mm"


def test_clearing_a_channels_own_diameter_removes_its_mark(channels_window: MainWindow) -> None:
    """Check that the mark goes once a channel follows the global diameter again.

    Applicator3 is given 3.0 mm, and its row must be bold before the clear. Fails if the row is
    still bold afterwards, keeps a background different from Applicator13's, or does not name
    the Channels Diameter it is now cut at. A stale mark would tell the clinician a needle is
    still custom when it is not.
    """
    model = channels_window.channelsmodel
    model.set_channel_diameter(UNMARKED_AGAIN_CHANNEL, 3.0)
    assert channel_item(channels_window, UNMARKED_AGAIN_CHANNEL).font().bold()

    model.clear_channel_diameter(UNMARKED_AGAIN_CHANNEL)
    cleared = channel_item(channels_window, UNMARKED_AGAIN_CHANNEL)
    reference = channel_item(channels_window, GLOBAL_DIAMETER_CHANNEL)

    assert not cleared.font().bold()
    assert cleared.background() == reference.background()
    assert cleared.toolTip() == reference.toolTip()


def test_a_disabled_channel_reads_disabled_and_stays_in_the_list(channels_window: MainWindow) -> None:
    """Check that a disabled channel stays listed and reads as disabled, even with its own diameter.

    Applicator7 is given 3.0 mm and then disabled. Fails if its status is not DISABLED, if its
    row does not say it is not cut, is not italic, or looks like a row with its own diameter.
    This is FR-CN-16's interface test case. A disabled needle has no hole in the printed
    cylinder, and before this change its row looked exactly like an enabled one.
    """
    from windows.models.channels_model import ChannelStatus

    model = channels_window.channelsmodel
    model.set_channel_diameter(DISABLED_CHANNEL, 3.0)
    model.toggle_channel_enabled(DISABLED_CHANNEL)
    disabled = channel_item(channels_window, DISABLED_CHANNEL)

    assert model.channel_status(DISABLED_CHANNEL) is ChannelStatus.DISABLED
    assert disabled.toolTip() == "Disabled, not cut into the cylinder"
    assert disabled.font().italic() and not disabled.font().bold()
    assert disabled.background() != channel_item(channels_window, MARKED_CHANNEL).background()


def test_the_tandem_channel_reads_tandem_in_the_list(cylinder_window: MainWindow) -> None:
    """Check that the tandem channel reads as the tandem, not as merely disabled.

    Applicator12 is set as the tandem, which also disables it. Fails if its status is not
    TANDEM, or its row is not bold italic with the tandem tooltip. The tandem channel is not
    cut as a needle, but the clinician must be able to tell it from a needle they switched off.
    A fresh window keeps tandem and disabled state out of the shared channel fixture.
    """
    from classes.dicom.fileio import read_dicom_folder
    from windows.models.channels_model import ChannelStatus

    plan = Path(__file__).resolve().parents[2] / "SI_C_D30 Brachify_Ex1"
    cylinder_window.dicommodel.update(read_dicom_folder(str(plan)))
    cylinder_window.navigationmodel.views[CHANNELS_TAB].create_channels_list()
    model = cylinder_window.channelsmodel
    model.set_tandem(TANDEM_CHANNEL)
    tandem = channel_item(cylinder_window, TANDEM_CHANNEL)

    assert model.channel_status(TANDEM_CHANNEL) is ChannelStatus.TANDEM
    assert tandem.toolTip() == "Tandem channel, not cut as a needle"
    assert tandem.font().bold() and tandem.font().italic()
