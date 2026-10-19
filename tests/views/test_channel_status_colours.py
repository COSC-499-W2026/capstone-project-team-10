"""Exercise how each row of the Channels list shows its channel's status."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtWidgets import QListWidgetItem

    from windows.main_window import MainWindow

CHANNELS_TAB = 2
GLOBAL_DIAMETER_CHANNEL = "Applicator13"

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
    from pathlib import Path

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
