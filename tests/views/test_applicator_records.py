"""Pin what ChannelsModel keeps for each applicator through a rename, so that keeping it in one place changes no behaviour."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from classes.mesh.helper import CustomNeedleSpec
from windows.models.channels_model import ChannelStatus

if TYPE_CHECKING:
    from windows.main_window import MainWindow

CHANNELS_TAB = 2
PLAN_APPLICATOR = "Applicator6"


def spec(label: str, x: float = 3.0) -> CustomNeedleSpec:
    """Make a straight spec at (x, -2) with Length 1 of 40 and Length 2 of 25. A helper, not a test."""
    return CustomNeedleSpec(label=label, x=x, y=-2.0, length1=40.0, length2=25.0)


@pytest.fixture
def restored_plan(channels_window: MainWindow) -> Iterator[None]:
    """Clear the tandem and reload the imported plan after a test that renames a plan applicator. A fixture, not a test.

    The window is shared by every test in this file, so a plan applicator renamed or made the
    tandem by one test would be different in the next. Loading the plan again rebuilds every
    plan applicator, as a new import does.
    """
    yield
    channels_window.channelsmodel.set_tandem(None)
    channels_window.channelsmodel.load_data(channels_window.dicommodel.data)
    channels_window.navigationmodel.views[CHANNELS_TAB].create_channels_list()


def test_a_renamed_tandem_stays_the_tandem_and_out_of_the_cut(channels_window: MainWindow, restored_plan: None) -> None:
    """Check renaming the applicator chosen as the tandem keeps it the tandem, uncut and undrawn, under its new name only.

    Fails if the new name loses the tandem status or the disabled state that keeps it out of the
    export cut and the 3D view, or if the old name is still reported disabled. A tandem that
    became a needle again would have a needle hole cut along the tandem's path in the printed
    cylinder.
    """
    model = channels_window.channelsmodel
    model.set_tandem(PLAN_APPLICATOR)

    model.edit_channel(PLAN_APPLICATOR, replace(model.spec_for_edit(PLAN_APPLICATOR), label="Renamed Tandem"))

    assert model.channel_status("Renamed Tandem") == ChannelStatus.TANDEM and model.is_channel_disabled("Renamed Tandem")
    assert "Renamed Tandem" not in [channel.label for channel in model.get_visible_channels()]
    assert "Renamed Tandem" not in channels_window.displaymodel.shapes
    assert not model.is_channel_disabled(PLAN_APPLICATOR) and not model.is_channel_tandem(PLAN_APPLICATOR)


def test_after_a_rename_every_change_reaches_the_applicator_by_its_new_name(channels_window: MainWindow) -> None:
    """Check disabling, enabling, giving and clearing an own diameter, and removing all work on the new name after a rename.

    Fails if any of them still finds the applicator under its old name, or raises KeyError on the
    new one. The clinician would press Disable or Remove on the renamed row and the printed
    cylinder would keep, or lose, a hole they did not choose.
    """
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator94"))
    model.edit_channel("Custom Applicator94", spec("Renamed Applicator94"))

    model.toggle_channel_enabled("Renamed Applicator94")
    disabled = model.channel_status("Renamed Applicator94")
    model.toggle_channel_enabled("Renamed Applicator94")
    model.set_channel_diameter("Renamed Applicator94", 4.5)
    own = model.channel_status("Renamed Applicator94"), model.channels["Renamed Applicator94"].get_diameter()
    model.clear_channel_diameter("Renamed Applicator94")
    cleared = model.channel_status("Renamed Applicator94")
    model.remove_channel("Renamed Applicator94")

    assert disabled == ChannelStatus.DISABLED and own == (ChannelStatus.OWN_DIAMETER, 4.5)
    assert cleared == ChannelStatus.STANDARD
    assert "Renamed Applicator94" not in model.channels and not model.is_custom_needle("Renamed Applicator94")
    assert "Custom Applicator94" not in model.channels and not model.is_custom_needle("Custom Applicator94")


def test_a_renamed_applicator_is_drawn_under_its_new_name_only(channels_window: MainWindow) -> None:
    """Check the 3D view holds the renamed applicator's new solid under the new name, and nothing under the old one.

    Fails if the old name keeps a shape, or the new name has none or holds the old solid. The
    viewport would draw a needle the list no longer has, or not draw one the export cuts, so
    the clinician would check a model that differs from the printed device.
    """
    model = channels_window.channelsmodel
    shapes = channels_window.displaymodel.shapes
    model.add_custom_needle(spec("Custom Applicator95"))

    new = model.edit_channel("Custom Applicator95", spec("Renamed Applicator95", x=-4.0))
    try:
        assert "Custom Applicator95" not in shapes
        assert shapes["Renamed Applicator95"].shape.IsSame(new.shape())
    finally:
        model.remove_channel("Renamed Applicator95")
