"""Exercise adding a custom applicator on the Channels tab: the model, the dialog, the list, the 3D shape and the export."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopoDS import TopoDS_Shape
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from classes.mesh.helper import CustomNeedleError, CustomNeedleSpec

if TYPE_CHECKING:
    from windows.main_window import MainWindow

CHANNELS_TAB = 2
EXPORT_TAB = 4


def spec(label: str, x: float = 3.0, y: float = -2.0) -> CustomNeedleSpec:
    """Make a spec with Length 1 of 40 and Length 2 of 25, at (3, -2) unless told otherwise. A helper, not a test."""
    return CustomNeedleSpec(label=label, x=x, y=y, length1=40.0, length2=25.0)


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in mm cubed from OpenCASCADE's mass properties. A helper, not a test."""
    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return properties.Mass()


def test_an_added_applicator_is_visible_and_its_solid_opens_through_the_base(channels_window: MainWindow) -> None:
    """Check the new channel is in the model and visible, with the spec's points and a solid from below the base to 65 mm plus dead space.

    Fails if the label is not a key of channels, the channel is missing from get_visible_channels,
    its points differ from [[3, -2, 65], [3, -2, 0]], the solid stops at the base, or the dead
    space is not added at the tissue end like an imported needle. A blind hole cannot be
    threaded, and a short tip changes how far a printed needle sits in the patient.
    """
    from classes.app import get_app

    model = channels_window.channelsmodel
    channel = model.add_custom_needle(spec("Custom Applicator90"))
    box = Bnd_Box()
    box.SetGap(0)
    brepbndlib.Add(channel.shape(), box, False)
    _, _, low, _, _, high = box.Get()

    assert model.channels["Custom Applicator90"] is channel and channel in model.get_visible_channels()
    assert [list(point) for point in channel.get_points()] == [[3.0, -2.0, 65.0], [3.0, -2.0, 0.0]]
    assert low < 0
    assert high == pytest.approx(65.0 + get_app().values.config_values["CONFIG_DEADSPACE"], abs=0.1)


def test_the_export_cut_removes_the_new_needle_from_the_cylinder(channels_window: MainWindow) -> None:
    """Check ExportView's final mesh loses at least 100 mm cubed once the applicator is added.

    Fails if the new applicator is not part of the cut, so the printed cylinder keeps solid
    material where the clinician asked for a channel. A 71 mm needle alone would remove about
    500, but Ex1's own holes cover part of this spot (197 measured), so the floor is 100, which
    an omitted needle, removing 0, cannot meet.
    """
    export_view = channels_window.navigationmodel.views[EXPORT_TAB]
    before = volume(export_view._final_mesh())

    channels_window.channelsmodel.add_custom_needle(spec("Custom Applicator92", x=-5.0, y=5.0))

    assert before - volume(export_view._final_mesh()) > 100.0


def test_the_reference_sheet_lists_the_new_applicator_with_its_own_number(channels_window: MainWindow) -> None:
    """Check the sheet keeps the applicator and gives it a channel number no imported channel has.

    Fails if the sheet drops it, or its number is blank or repeats an imported one. The sheet
    is what the clinician reads to thread each needle, so two needles with one number could be
    threaded into each other's holes.
    """
    from classes.pdf.template_reference import channels_inside_cylinder

    model = channels_window.channelsmodel
    imported_numbers = [channel.channel_number for channel in model.channels.values()]
    channel = model.add_custom_needle(spec("Custom Applicator93", x=0.0, y=6.0))

    assert channel in channels_inside_cylinder([channel], channels_window.cylindermodel.cylinder.diameter)
    assert channel.channel_number.isdigit() and channel.channel_number not in imported_numbers


@pytest.mark.parametrize("label, text", [("", "Name"), ("   ", "Name"), (None, "already")])
def test_an_empty_or_repeated_name_is_refused_and_changes_nothing(channels_window: MainWindow, label: str | None, text: str) -> None:
    """Check an empty, blank or imported name raises CustomNeedleError and leaves the channels as they were.

    Fails if the model accepts it. Channels is keyed by label, so a repeat would replace an
    imported needle and delete a needle the plan asked for from the printed model.
    """
    model = channels_window.channelsmodel
    label = next(iter(model.channels)) if label is None else label
    before = dict(model.channels)

    with pytest.raises(CustomNeedleError, match=text):
        model.add_custom_needle(spec(label))

    assert model.channels == before


def test_an_applicator_cannot_be_added_before_a_plan_is_imported(cylinder_window: MainWindow) -> None:
    """Check a window with no plan refuses the applicator and its Add button is disabled.

    Fails if the model accepts one or the button is enabled. The plan sets the cylinder length
    the heights are measured against, so a needle added without it would jump by the whole
    cylinder length the first time the length is applied.
    """
    view = cylinder_window.navigationmodel.views[CHANNELS_TAB]

    with pytest.raises(CustomNeedleError, match="plan"):
        cylinder_window.channelsmodel.add_custom_needle(spec("Custom Applicator95"))

    assert not view.btn_add_applicator.isEnabled()


def test_a_needle_added_after_a_length_change_keeps_its_tip_where_it_was_typed(channels_window: MainWindow) -> None:
    """Check with the cylinder 20 mm longer the tip is at 65, and a later change to 30 mm moves it to 75.

    Fails if the tip lands at 85, which double counts the change, or does not follow the later
    one. Points are kept in the plan's frame and the Channels offset moves them, so a needle
    that ignored the offset would sit in the wrong place on a patient's applicator.
    """
    model = channels_window.channelsmodel
    model.update_height_offset(20.0)
    try:
        channel = model.add_custom_needle(spec("Custom Applicator96"))
        assert channel.get_points()[0][2] == 65.0
        model.update_height_offset(30.0)
        assert channel.get_points()[0][2] == 75.0
    finally:
        model.update_height_offset(0.0)


class StubbedForm:
    """Stand in for the Add Applicator dialog, as a helper and not a test.

    Assigned to ChannelsView.ask_needle, the view's seam for its dialog, so no module is
    patched. It records the label the view suggested and gives the chosen answer, None
    meaning Cancel.
    """

    def __init__(self, answer: CustomNeedleSpec | None) -> None:
        """Remember the answer to give, None meaning Cancel. A helper, not a test."""
        self.answer = answer
        self.suggested: list[str] = []

    def __call__(self, label: str) -> CustomNeedleSpec | None:
        """Record the suggested label and return the chosen answer. A helper, not a test."""
        self.suggested.append(label)
        return self.answer


def test_add_applicator_offers_the_first_free_name_and_adds_a_row_and_cancel_adds_nothing(channels_window: MainWindow) -> None:
    """Check the Add button suggests the first free Custom Applicator name, adds a row and channel on an answer, and nothing on Cancel.

    Fails if the button is not wired, the suggestion repeats a name in use, the list is not
    rebuilt, or Cancel adds a channel. A needle with no row cannot be selected, disabled or
    given its own diameter, and a cancelled dialog must not leave an empty applicator.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    before = len(model.channels)
    view.ask_needle = StubbedForm(None)
    QTest.mouseClick(view.btn_add_applicator, Qt.MouseButton.LeftButton)
    assert len(model.channels) == before

    expected = next(f"Custom Applicator{n}" for n in range(1, 1000) if f"Custom Applicator{n}" not in model.channels)
    stub = view.ask_needle = StubbedForm(spec(expected))
    QTest.mouseClick(view.btn_add_applicator, Qt.MouseButton.LeftButton)

    assert stub.suggested == [expected]
    assert len(model.channels) == before + 1 and view.ui.listwidget_channels.count() == before + 1
    assert view.ui.listwidget_channels.findItems(expected, Qt.MatchFlag.MatchExactly)


def test_the_dialog_stays_open_with_the_reason_on_bad_numbers_and_hands_back_good_ones(channels_window: MainWindow) -> None:
    """Check OK with a start outside the base keeps the dialog open showing the model's text, and valid numbers come back unchanged.

    Fails if the dialog closes on bad numbers, shows other words than the model's, or reads a
    field into the wrong parameter, such as X and Y swapped, which would mirror the needle
    across the cylinder on the printed applicator.
    """
    from windows.views.channels_view import AddApplicatorDialog

    dialog = AddApplicatorDialog("Custom Applicator99", channels_window.channelsmodel.custom_needle_error)
    ok = dialog.buttons.button(QDialogButtonBox.StandardButton.Ok)
    dialog.spin_x.setValue(50.0)
    QTest.mouseClick(ok, Qt.MouseButton.LeftButton)
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert "base" in dialog.label_error.text() and not dialog.label_error.isHidden()

    dialog.edit_label.setText("Left needle")
    dialog.spin_x.setValue(4.0)
    dialog.spin_y.setValue(-6.0)
    dialog.spin_length1.setValue(30.0)
    dialog.spin_length2.setValue(12.5)
    QTest.mouseClick(ok, Qt.MouseButton.LeftButton)

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.spec() == CustomNeedleSpec(label="Left needle", x=4.0, y=-6.0, length1=30.0, length2=12.5)
