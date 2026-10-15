from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDoubleSpinBox, QStyle

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
                  ui.sb_threading_diameter)

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
    finally:
        values.config_values = live_settings

    assert model.channels[OWN_DIAMETER_CHANNEL].get_diameter() == 3.2
    assert model.channels[GLOBAL_DIAMETER_CHANNEL].get_diameter() == 2.5


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

    assert model.channels[CLEARED_CHANNEL].get_diameter() == model.diameter
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
