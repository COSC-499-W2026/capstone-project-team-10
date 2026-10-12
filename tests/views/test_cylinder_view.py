from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PySide6.QtWidgets import QComboBox

if TYPE_CHECKING:
    from windows.main_window import MainWindow
    from windows.views.cylinder_view import CylinderView


def choose_units(view: CylinderView, unit: str) -> None:
    """Select the real units control, failing if the requested option is missing.

    This helper drives the signal wired by the view so conversion wiring is exercised.
    A missing control or option fails an assertion rather than silently skipping the edit.
    """
    selector = view.findChild(QComboBox, "combobox_units")
    assert selector is not None, "Cylinder needs a units selector"
    index = selector.findText(unit)
    assert index >= 0, f"Cylinder needs the {unit} option"
    selector.setCurrentIndex(index)


def test_centimetres_display_all_four_fields_with_scaled_limits(cylinder_window: MainWindow) -> None:
    """Check all Cylinder values, suffixes, steps and limits after selecting cm.

    Wrong scaling fails literal assertions, preventing a 16 cm cylinder being interpreted
    as 16 mm or the 60–300 mm length range being lost.
    """
    view = cylinder_window.navigationmodel.views[1]
    view.ui.spinbox_base_thickness.setValue(3)
    view.ui.spinbox_base_height.setValue(10)
    choose_units(view, "cm")
    fields = (view.ui.spinbox_diameter, view.ui.spinbox_length,
              view.ui.spinbox_base_thickness, view.ui.spinbox_base_height)
    assert [field.value() for field in fields] == [3.0, 16.0, 0.3, 1.0]
    assert [field.suffix() for field in fields] == [" cm"] * 4
    assert [field.singleStep() for field in fields] == [0.1] * 4
    assert view.ui.spinbox_length.minimum() == 6.0
    assert view.ui.spinbox_length.maximum() == 30.0
    assert view.ui.spinbox_diameter.maximum() == 9.999
    assert view.ui.spinbox_base_height.maximum() == 9.9


def test_switching_units_keeps_unapplied_edits_and_live_settings(cylinder_window: MainWindow) -> None:
    """Keep pending edits while switching mm/cm without applying settings or geometry.

    A reset to defaults or a model/config change fails these assertions. Merely changing
    display units must not alter the device a clinician has already designed.
    """
    from classes.app import get_app

    view = cylinder_window.navigationmodel.views[1]
    view.ui.spinbox_diameter.setValue(31.27)
    view.ui.spinbox_length.setValue(167)
    before = get_app().values.config_values.copy()
    for _ in range(20):
        choose_units(view, "cm")
        choose_units(view, "mm")
    assert view.ui.spinbox_diameter.value() == 31.27
    assert view.ui.spinbox_length.value() == 167
    assert get_app().values.config_values == before
    assert cylinder_window.cylindermodel.cylinder is None


def test_apply_centimetres_builds_and_exports_millimetres(cylinder_window: MainWindow) -> None:
    """Apply cm inputs and check the real cylinder, collar settings and config snapshot in mm.

    A missing conversion fails dimension assertions. A factor-of-ten geometry error would
    produce a wrongly sized applicator for the patient.
    """
    from classes.app import get_app
    from settings.reset import getCurrentValues

    view = cylinder_window.navigationmodel.views[1]
    choose_units(view, "cm")
    view.ui.spinbox_diameter.setValue(3.125)
    view.ui.spinbox_length.setValue(17.3)
    view.ui.spinbox_base_thickness.setValue(0.3)
    view.ui.spinbox_base_height.setValue(1.2)
    view.ui.cb_add_base.setChecked(True)
    view.action_apply_settings()
    cylinder = cylinder_window.cylindermodel.cylinder
    assert cylinder.diameter == 31.25
    assert cylinder.length == 173.0
    assert cylinder.expand_base
    assert get_app().values.config_values["CONFIG_BASE_THICKNESS"] == 3.0
    assert get_app().values.config_values["CONFIG_BASE_HEIGHT"] == 12.0
    snapshot = getCurrentValues()
    assert snapshot["CONFIG_CYLINDER_DIAMETER"] == 31.25
    assert snapshot["CONFIG_CYLINDER_LENGTH"] == 173.0
    assert view.ui.spinbox_length.value() == 17.3
    assert cylinder_window.navigationmodel.views[3].ui.sb_tandem_height.maximum() == 173.0


@pytest.mark.parametrize("existing_cylinder", [False, True])
def test_config_reset_in_centimetres_keeps_mm_values(
    cylinder_window: MainWindow, existing_cylinder: bool,
) -> None:
    """Load mm configuration values while the Cylinder display is in cm, before or after Apply.

    Wrong display or reapplied cylinder dimensions fail literal assertions. Loading a file
    must not multiply the device's size by ten because of the selected unit.
    """
    from classes.app import get_app
    from settings.reset import resetAllValues

    view = cylinder_window.navigationmodel.views[1]
    if existing_cylinder:
        view.action_apply_settings()
    choose_units(view, "cm")
    config = get_app().values.config_values.copy()
    config["CONFIG_CYLINDER_DIAMETER"] = 32.5
    config["CONFIG_CYLINDER_LENGTH"] = 175.25
    get_app().values.config_values = config
    resetAllValues(config)
    assert view.ui.spinbox_diameter.value() == 3.25
    assert view.ui.spinbox_length.value() == 17.5
    choose_units(view, "mm")
    choose_units(view, "cm")
    view.action_apply_settings()
    assert cylinder_window.cylindermodel.cylinder.length == 175.25
    assert cylinder_window.cylindermodel.cylinder.diameter == 32.5


def test_dicom_import_in_centimetres_keeps_the_model_and_needle_coordinates_in_mm(
    cylinder_window: MainWindow,
) -> None:
    """Import Ex1 in cm display and confirm the cylinder and offset remain in mm.

    Wrong UI scaling or height conversion fails the assertions. Needle positions must
    stay aligned with the cylinder and retain their original DICOM coordinates.
    """
    from classes.dicom.fileio import read_dicom_folder

    view = cylinder_window.navigationmodel.views[1]
    choose_units(view, "cm")
    plan = read_dicom_folder(str(Path(__file__).resolve().parents[2] / "SI_C_D30 Brachify_Ex1"))
    cylinder_window.cylindermodel.starting_length = 160.0
    cylinder_window.dicommodel.update(plan)
    assert view.ui.spinbox_diameter.value() == 3.0
    assert view.ui.spinbox_length.value() == 16.0
    channel = cylinder_window.channelsmodel.get_visible_channels()[0]
    original = [point.copy() for point in channel.points]
    view.ui.spinbox_length.setValue(17.0)
    view.action_apply_settings()
    assert channel.points == original
    assert channel.get_points()[0][2] == pytest.approx(original[0][2] + 10.0)


def test_cm_length_limits_clamp_before_apply(cylinder_window: MainWindow) -> None:
    """Reject display lengths outside 6–30 cm through the real spin box's bounds.

    Unscaled bounds fail the clamped values. The clinical 60–300 mm range must apply
    equally in either unit before a cylinder can be built.
    """
    view = cylinder_window.navigationmodel.views[1]
    choose_units(view, "cm")
    view.ui.spinbox_length.setValue(5.0)
    assert view.ui.spinbox_length.value() == 6.0
    view.ui.spinbox_length.setValue(31.0)
    assert view.ui.spinbox_length.value() == 30.0


def test_a_new_window_starts_in_mm(cylinder_window: MainWindow) -> None:
    """Check the startup unit and dimensions in a fresh window.

    An unexpected cm default fails the selector/value assertions. Units are a display
    preference for this window and must not be stored in the shared configuration.
    """
    view = cylinder_window.navigationmodel.views[1]
    selector = view.findChild(QComboBox, "combobox_units")
    assert selector is not None, "Cylinder needs a units selector"
    assert selector.currentText() == "mm"
    assert view.ui.spinbox_diameter.value() == 30.0
    assert view.ui.spinbox_length.value() == 160.0
