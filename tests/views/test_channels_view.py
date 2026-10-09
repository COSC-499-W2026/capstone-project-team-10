from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
