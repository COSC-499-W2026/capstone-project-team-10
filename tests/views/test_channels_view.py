from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDoubleSpinBox, QStyle

    from windows.main_window import MainWindow

CYLINDER_TAB = 1
CHANNELS_TAB = 2
FIRST_CHANNEL = "Applicator2"


def select_first_channel_then_leave_and_return(window: MainWindow) -> None:
    """Open the Channels tab, pick its first channel, go to the Cylinder tab and come back.

    A helper, not a test. It is the user's sequence from the bug report, driven through the
    real navigation signal. setCurrentRow emits currentItemChanged, the same signal a mouse
    click on the list emits, so the view and model react exactly as they do to a click.
    """
    # Imported here, not at the top: importing classes at collection time would fix
    # ~/brachify to the real home folder before the channels_window fixture redirects HOME.
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
