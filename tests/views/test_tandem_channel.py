"""Exercise how the tandem channel reaches the tandem: chosen at import, and cleared with set_tandem(None)."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from windows.main_window import MainWindow

FORMER_TANDEM = "Applicator12"


def test_clearing_the_tandem_channel_makes_it_a_needle_again(channels_window: MainWindow) -> None:
    """Check that clearing the tandem channel leaves no tandem and enables the channel again.

    Applicator12 is made the tandem, then the tandem is cleared with set_tandem(None). Fails if
    the plan still names a tandem channel, if Applicator12 stays disabled, or if None is put in
    the disabled list. A channel left disabled would get no hole in the printed cylinder, and
    nothing would show why, because it is no longer the tandem either.
    """
    model = channels_window.channelsmodel
    model.set_tandem(FORMER_TANDEM)

    model.set_tandem(None)

    assert channels_window.dicommodel.data.tandem_channel is None
    assert model.disabled_channels == []


def test_clearing_the_tandem_channel_keeps_the_tandem_rotation(channels_window: MainWindow) -> None:
    """Check that clearing the tandem channel leaves the tandem pointing where it pointed.

    Applicator12 is made the tandem, which aims the tandem along its tip, then the tandem
    channel is cleared. Fails if the rotation changes, as it did when set_tandem_channel set it
    to 0 and then raised AttributeError on the missing channel. A generated tandem would swing
    to a direction nobody chose, and the cut would no longer match the Rotation box.
    """
    model = channels_window.channelsmodel
    model.set_tandem(FORMER_TANDEM)
    aimed = channels_window.tandemmodel.rotation

    model.set_tandem(None)

    assert aimed != 0.0
    assert channels_window.tandemmodel.rotation == aimed


def test_importing_a_plan_with_a_tandem_channel_aims_the_tandem_along_it(tandem_window: MainWindow) -> None:
    """Check that importing Ex2 takes the tandem's rotation from its channel 14, named Tandem.

    Ex2's Tandem tip lies on the +x side, so its direction is 359.996 degrees. Fails if the
    rotation or the plan rotation the warning compares against is not 359.996, or if the plan
    is not recorded as having a tandem. That happened when set_tandem_channel raised NameError
    for a channel named Tandem, which Qt prints and ignores, so the tandem stayed at the
    default 0 degrees and the rotation warning never fired.
    """
    tandem = tandem_window.tandemmodel

    assert tandem.rotation == pytest.approx(359.996, abs=0.001)
    assert tandem.protation == pytest.approx(359.996, abs=0.001)
    assert tandem.hasTandemInDICOM
