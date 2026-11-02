"""Exercise how each row of the Channels list shows its channel's status."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
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
    assert marked.toolTip() == "Own diameter 3.000 mm\nDouble click to move"


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
    assert disabled.toolTip() == "Disabled, not cut into the cylinder\nDouble click to move"
    assert disabled.font().italic() and not disabled.font().bold()
    assert disabled.background() != channel_item(channels_window, MARKED_CHANNEL).background()


def listed_labels(window: MainWindow) -> list[str]:
    """Return the labels of the Channels list's rows, top to bottom. A helper, not a test."""
    channel_list = window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels
    return [channel_list.item(row).text() for row in range(channel_list.count())]


def test_the_tandem_channel_leaves_the_list_and_comes_back_as_a_needle(cylinder_window: MainWindow) -> None:
    """Check the tandem channel is not listed, and is listed again, plain, once it is not the tandem.

    Applicator12 is set as the tandem, then the tandem is cleared. Fails if Applicator12 still has
    a row while it is the tandem, or has no row, or a styled one, afterwards. Nothing on the
    Channels tab applies to the tandem channel, and Enable on its row cut it as a needle as well
    as labelling the tandem hole with its number. A fresh window keeps this out of the shared
    channel fixture.
    """
    from pathlib import Path

    from classes.dicom.fileio import read_dicom_folder

    plan = Path(__file__).resolve().parents[2] / "SI_C_D30 Brachify_Ex1"
    cylinder_window.dicommodel.update(read_dicom_folder(str(plan)))
    cylinder_window.navigationmodel.views[CHANNELS_TAB].create_channels_list()
    model = cylinder_window.channelsmodel

    model.set_tandem(TANDEM_CHANNEL)
    assert TANDEM_CHANNEL not in listed_labels(cylinder_window)
    assert len(listed_labels(cylinder_window)) == 11

    model.set_tandem(None)
    returned = channel_item(cylinder_window, TANDEM_CHANNEL)
    assert not returned.font().bold() and not returned.font().italic()
    assert returned.background() == channel_item(cylinder_window, GLOBAL_DIAMETER_CHANNEL).background()


def test_ex2_lists_every_channel_except_its_tandem(tandem_window: MainWindow) -> None:
    """Check that after importing Ex2 the list shows Applicator2 to Applicator13 and not Tandem.

    Fails if channel 14, Tandem, has a row, a needle is missing, or the legend under the list
    still explains a tandem row. The tandem channel is chosen on the Tandem tab, so a row for it
    here would offer controls that do not apply to it, and a legend for a row that never appears
    would send the clinician looking for it.
    """
    legend = tandem_window.navigationmodel.views[CHANNELS_TAB].ui.label_channel_status_legend.text()

    assert listed_labels(tandem_window) == [f"Applicator{number}" for number in range(2, 14)]
    assert "tandem" not in legend.lower()


def test_the_tandem_channel_cannot_be_enabled_as_a_needle(tandem_window: MainWindow) -> None:
    """Check toggle_channel_enabled refuses the tandem channel with ValueError and leaves it disabled.

    Fails if Tandem is enabled. It would then be cut as a 2.7 mm needle hole beside the tandem
    hole, and listed on the reference sheet as a needle while its number labels the tandem.
    """
    model = tandem_window.channelsmodel

    with pytest.raises(ValueError):
        model.toggle_channel_enabled("Tandem")

    assert model.is_channel_disabled("Tandem")
