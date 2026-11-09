"""Exercise the check that a custom applicator's numbers give a channel the export can cut out of the cylinder."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopoDS import TopoDS_Shape
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from classes.mesh.helper import CustomNeedleError, CustomNeedleSpec

if TYPE_CHECKING:
    from windows.main_window import MainWindow

EXPORT_TAB = 4


def bent(label: str, phi: float) -> CustomNeedleSpec:
    """Make a needle from (-9, -6) straight up 100 mm, then a 30 degree bend of radius 20 towards phi, then 25 mm. A helper, not a test."""
    return CustomNeedleSpec(label=label, x=-9.0, y=-6.0, length1=100.0, length2=25.0, radius=20.0, theta=30.0, phi=phi)


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in mm cubed from OpenCASCADE's mass properties. A helper, not a test."""
    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return properties.Mass()


def test_numbers_the_export_cannot_cut_are_refused_in_plain_text_and_change_nothing(channels_window: MainWindow) -> None:
    """Check the bend towards Phi 90 from (-9, -6) in Ex1 raises CustomNeedleError for an add and for an edit, and nothing changes.

    Fails if the numbers are accepted. OpenCASCADE builds a valid solid for them but cutting it
    out of the cylinder returns a warning and removes 33 mm cubed instead of about 811, so the
    printed cylinder would have no channel for a needle the clinician placed, and nothing on
    the screen would say so. It also fails if the text has a colon or an em dash, which
    AGENTS.md bans in copy a clinician reads. The numbers were found by probe with pythonocc
    7.7.2, the pinned version, so a change of version may need new ones.
    """
    model = channels_window.channelsmodel
    kept = model.add_custom_needle(bent("Custom Applicator71", phi=45.0))
    before = dict(model.channels)

    try:
        with pytest.raises(CustomNeedleError, match="cut") as add_refusal:
            model.add_custom_needle(bent("Custom Applicator72", phi=90.0))
        with pytest.raises(CustomNeedleError, match="cut"):
            model.edit_channel("Custom Applicator71", bent("Custom Applicator71", phi=90.0))

        assert model.channels == before and model.channels["Custom Applicator71"] is kept
        assert ":" not in str(add_refusal.value) and "—" not in str(add_refusal.value)
    finally:
        model.remove_channel("Custom Applicator71")  # leaves the spot free for the next test, which measures a volume there


def test_the_same_bend_towards_another_direction_is_accepted_and_the_export_loses_its_volume(channels_window: MainWindow) -> None:
    """Check the bend towards Phi 45 is accepted and the export loses more than 500 mm cubed to it.

    Fails if the check refuses numbers that cut cleanly, which would take away a bend the
    clinician is allowed to print, or accepts them but the cut removes nothing. Phi 45 removes
    about 811, so the floor of 500 is far from the 33 that a failed cut removes.
    """
    export_view = channels_window.navigationmodel.views[EXPORT_TAB]
    before = volume(export_view._final_mesh())

    channels_window.channelsmodel.add_custom_needle(bent("Custom Applicator73", phi=45.0))

    assert before - volume(export_view._final_mesh()) > 500.0


def test_the_form_stays_open_with_the_cut_reason_for_those_numbers(channels_window: MainWindow) -> None:
    """Check OK with the failing numbers keeps the form open and shows the model's reason under the fields.

    Fails if the form closes, which would hand the view numbers the model then refuses, or shows
    no reason, which leaves the clinician with a form that does nothing and no idea why.
    """
    from windows.views.add_applicator_dialog import AddApplicatorDialog

    dialog = AddApplicatorDialog("Custom Applicator74", channels_window.channelsmodel.custom_needle_error)
    for spin, value in ((dialog.spin_x, -9.0), (dialog.spin_y, -6.0), (dialog.spin_length1, 100.0), (dialog.spin_length2, 25.0),
                        (dialog.spin_radius, 20.0), (dialog.spin_theta, 30.0), (dialog.spin_phi, 90.0)):
        spin.setValue(value)

    QTest.mouseClick(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok), Qt.MouseButton.LeftButton)

    assert dialog.result() != QDialog.DialogCode.Accepted
    assert "cut" in dialog.label_error.text() and not dialog.label_error.isHidden()
