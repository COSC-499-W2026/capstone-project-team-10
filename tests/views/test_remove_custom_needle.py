"""Exercise removing an applicator, plan or custom, on the Channels tab: the model rules and the Remove Applicator button."""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopoDS import TopoDS_Shape
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from classes.mesh.helper import CustomNeedleError, CustomNeedleSpec

if TYPE_CHECKING:
    from windows.main_window import MainWindow

CHANNELS_TAB = 2
EXPORT_TAB = 4


def spec(label: str, x: float = 3.0) -> CustomNeedleSpec:
    """Make a straight spec at (x, -2) with Length 1 of 40 and Length 2 of 25. A helper, not a test."""
    return CustomNeedleSpec(label=label, x=x, y=-2.0, length1=40.0, length2=25.0)


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in mm cubed from OpenCASCADE's mass properties. A helper, not a test."""
    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return properties.Mass()


@pytest.fixture
def restored_plan(channels_window: MainWindow) -> Iterator[None]:
    """Reload the imported plan after a test that removes a plan applicator. A fixture, not a test.

    The window is shared by every test in this file, so a plan applicator removed by one test
    would be missing from the next. Loading the plan again rebuilds every plan applicator.
    """
    yield
    channels_window.channelsmodel.load_data(channels_window.dicommodel.data)
    channels_window.navigationmodel.views[CHANNELS_TAB].create_channels_list()


def test_removing_a_custom_applicator_puts_the_export_cut_back_as_it_was(channels_window: MainWindow) -> None:
    """Check the export volume with the applicator added and removed is the volume from before it was added.

    Fails if the channel stays in the model, so the printed cylinder keeps a hole the clinician
    deleted, or the removal takes a plan needle with it. A hole nobody sees on screen would be
    threaded into a patient's applicator.
    """
    model = channels_window.channelsmodel
    export_view = channels_window.navigationmodel.views[EXPORT_TAB]
    before = volume(export_view._final_mesh())
    model.add_custom_needle(spec("Custom Applicator81", x=-5.0))

    model.remove_channel("Custom Applicator81")

    assert "Custom Applicator81" not in model.channels and not model.is_custom_needle("Custom Applicator81")
    assert volume(export_view._final_mesh()) == pytest.approx(before, rel=1e-6)


def test_removing_clears_the_disabled_own_diameter_and_selected_state_of_the_label(channels_window: MainWindow) -> None:
    """Check a removed applicator that was disabled, selected and given its own diameter leaves none of that behind.

    Fails if any of the three keeps the label. A new applicator reusing the name would arrive
    disabled, and so be missing from the printed device, or with another needle's diameter.
    """
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator82"))
    model.toggle_channel_enabled("Custom Applicator82")
    model.set_channel_diameter("Custom Applicator82", 4.0)
    model.set_selected_channels("Custom Applicator82")

    model.remove_channel("Custom Applicator82")

    assert "Custom Applicator82" not in model.disabled_channels
    assert "Custom Applicator82" not in model.own_diameters
    assert "Custom Applicator82" not in model.selected_channels


def test_a_plan_applicator_can_be_removed_and_leaves_the_export_and_the_sheet(channels_window: MainWindow, restored_plan: None) -> None:
    """Check removing an imported applicator deletes it and every record of it, and spares the others.

    Fails if it is refused, if any of channels, disabled, own diameter or selection keeps the
    label, or if it stays among the channels the export cuts and the PDF lists, which both read
    get_visible_channels. The clinician would print a hole for a needle they deleted.
    """
    model = channels_window.channelsmodel
    label, *others = model.channels
    model.set_channel_diameter(label, 4.0)
    model.toggle_channel_enabled(label)
    model.set_selected_channels(label)

    model.remove_channel(label)

    assert label not in model.channels and label not in model.own_diameters
    assert label not in model.disabled_channels and label not in model.selected_channels
    assert list(model.channels) == others
    assert label not in [channel.label for channel in model.get_visible_channels()]


def test_removing_an_unknown_label_raises_key_error_and_changes_nothing(channels_window: MainWindow) -> None:
    """Check removing a label no applicator has raises KeyError and leaves the channels as they were.

    Fails if it passes silently or removes something else, so a stale list row would look
    removed while the printed device kept its needle.
    """
    model = channels_window.channelsmodel
    before = dict(model.channels)

    with pytest.raises(KeyError):
        model.remove_channel("No Such Applicator")

    assert model.channels == before


def test_the_applicator_chosen_as_the_tandem_cannot_be_removed(channels_window: MainWindow) -> None:
    """Check removing the custom applicator that is the tandem raises CustomNeedleError and keeps it.

    Fails if it is removed, because the plan still names it as the tandem and the next look for
    the tandem channel raises KeyError, which stops the Tandem tab and the export.
    """
    model = channels_window.channelsmodel
    data = channels_window.dicommodel.data
    model.add_custom_needle(spec("Custom Applicator80"))
    old_tandem, data.tandem_channel = data.tandem_channel, "Custom Applicator80"
    try:
        with pytest.raises(CustomNeedleError, match="tandem"):
            model.remove_channel("Custom Applicator80")
    finally:
        data.tandem_channel = old_tandem

    assert "Custom Applicator80" in model.channels


def test_the_remove_button_is_on_for_any_selected_applicator_that_is_not_the_tandem(channels_window: MainWindow) -> None:
    """Check Remove Applicator is off with nothing selected, on for a plan or a custom applicator, and off for the tandem.

    Fails if it is off for a plan needle, which leaves no way to drop a wrong one, off for
    a custom one, which leaves no way to remove it, on for the tandem, which the model refuses
    and leaves the press doing nothing, or if its style has no disabled look, since the buttons
    above it have none and an off button that looks live gets pressed again and again.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator85"))
    model.clear_selected_channels()
    off_when_none = not view.btn_remove_applicator.isEnabled()
    model.set_selected_channels(next(iter(model.channels)))
    on_for_plan = view.btn_remove_applicator.isEnabled()
    model.set_selected_channels("Custom Applicator85")
    on_for_custom = view.btn_remove_applicator.isEnabled()
    data = channels_window.dicommodel.data
    old_tandem, data.tandem_channel = data.tandem_channel, "Custom Applicator85"
    try:
        view.action_update_settings()
        off_for_tandem = not view.btn_remove_applicator.isEnabled()
    finally:
        data.tandem_channel = old_tandem

    assert off_when_none and on_for_plan and on_for_custom and off_for_tandem
    assert ":disabled" in view.btn_remove_applicator.styleSheet()


def test_the_remove_button_takes_the_selected_applicator_out_of_the_model_and_the_list(channels_window: MainWindow) -> None:
    """Check pressing Remove Applicator deletes the selected custom applicator and its list row, and selects nothing.

    Fails if the button is not wired, the row stays in the list, or the selection still names a
    channel that no longer exists. A row with no needle behind it crashes the next Disable or Move.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator86"))
    view.create_channels_list()
    model.set_selected_channels("Custom Applicator86")

    QTest.mouseClick(view.btn_remove_applicator, Qt.MouseButton.LeftButton)

    assert "Custom Applicator86" not in model.channels
    assert not view.ui.listwidget_channels.findItems("Custom Applicator86", Qt.MatchFlag.MatchExactly)
    assert model.get_selected_channel() is None


def test_removing_a_plan_applicator_asks_first_and_cancel_keeps_it(channels_window: MainWindow) -> None:
    """Check pressing Remove Applicator on a plan applicator asks once, and answering no removes nothing.

    Fails if it removes without asking, or still removes after a no. A plan applicator comes
    back only by importing the plan again, so a stray click would cost the clinician their edits.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    label = next(iter(model.channels))
    asked = []
    view.confirm_remove = lambda name: asked.append(name) or False
    model.set_selected_channels(label)

    QTest.mouseClick(view.btn_remove_applicator, Qt.MouseButton.LeftButton)

    assert asked == [label] and label in model.channels


def test_confirming_removes_a_plan_applicator_and_a_custom_one_is_never_asked_about(channels_window: MainWindow, restored_plan: None) -> None:
    """Check a yes removes the plan applicator and its list row, and a custom applicator goes without a question.

    Fails if a yes leaves the row or the channel, or if a custom applicator, which the Add
    Applicator button makes again in seconds, also asks and so slows every removal.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    label = next(iter(model.channels))
    asked = []
    view.confirm_remove = lambda name: asked.append(name) or True
    model.set_selected_channels(label)
    QTest.mouseClick(view.btn_remove_applicator, Qt.MouseButton.LeftButton)
    removed_plan = label not in model.channels and not view.ui.listwidget_channels.findItems(label, Qt.MatchFlag.MatchExactly)
    model.add_custom_needle(spec("Custom Applicator87"))
    view.create_channels_list()
    model.set_selected_channels("Custom Applicator87")

    QTest.mouseClick(view.btn_remove_applicator, Qt.MouseButton.LeftButton)

    assert removed_plan and asked == [label] and "Custom Applicator87" not in model.channels


def test_a_new_import_forgets_the_custom_applicators(channels_window: MainWindow) -> None:
    """Check loading the plan again leaves no custom applicator and no record of one.

    Fails if a record outlives its needle, because the Remove button would then treat a later
    plan applicator with the same name as a custom one and offer to delete it from the plan.
    """
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator89"))

    model.load_data(channels_window.dicommodel.data)

    assert "Custom Applicator89" not in model.channels and model.custom_specs == {}
