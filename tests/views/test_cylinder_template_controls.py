"""Exercise the cylinder template controls in the Cylinder tab's Templates group."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

if TYPE_CHECKING:
    from PySide6.QtWidgets import QPushButton

    from windows.main_window import MainWindow
    from windows.views.cylinder_view import CylinderView

CYLINDER_TAB = 1


def click(button: QPushButton) -> None:
    """Click a button with the left mouse button, the way a physicist does.

    A helper, not a test. QTest sends a real press and release, so every slot the view
    connected to the button runs, and a disabled button ignores the click.
    """
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)


def library_path() -> Path:
    """Return the cylinder template library inside this run's temporary home folder.

    A helper, not a test. units_app points HOME at a temporary folder before brachify is
    imported, so this never touches the developer's own ~/brachify.
    """
    from classes.info import USER_PATH
    from settings.cylinder_templates import LIBRARY_FILE_NAME

    return USER_PATH / LIBRARY_FILE_NAME


@pytest.fixture
def cylinder_tab(cylinder_window: MainWindow) -> Iterator[CylinderView]:
    """Give each test the real Cylinder tab with an empty template library.

    A fixture, not a test. The library file outlives a window, so it is deleted before and
    after each test, and the tab rereads it, so no test sees another test's templates.
    """
    library_path().unlink(missing_ok=True)
    view = cylinder_window.navigationmodel.views[CYLINDER_TAB]
    view.action_load_templates()
    yield view
    library_path().unlink(missing_ok=True)


def save_as(view: CylinderView, name: str, note: str = "") -> None:
    """Type a name and a note and press Save as Template, as a helper and not a test."""
    view.ui.le_template_name.setText(name)
    view.ui.le_template_note.setText(note)
    click(view.ui.btn_save_template)


def test_save_as_template_lists_the_template_and_writes_it(cylinder_tab: CylinderView) -> None:
    """Check that Save as Template adds the tab's settings to the list and to the library file.

    The tab shows the default 30 mm by 160 mm dome cylinder. Fails if "Standard 30" is not
    listed, the file does not hold the 11 default settings with its name and note, the row's
    tooltip does not summarise it, or the status line does not confirm the save. A template
    that is only listed is lost when brachify closes, and FR-CN-05 asks for one the physicist
    can use later.
    """
    from settings.cylinder_templates import CylinderDesign, load_templates

    save_as(cylinder_tab, "Standard 30", "Clinic default")

    [saved] = load_templates(library_path())
    assert (saved.name, saved.note) == ("Standard 30", "Clinic default")
    assert saved.design == CylinderDesign(30.0, 160.0, False, 0.0, 0.0, True, 0.0, 2.0, 1.8, 10.0, False)
    row = cylinder_tab.ui.list_templates.item(0)
    assert row.text() == "Standard 30"
    assert "Clinic default" in row.toolTip() and "30.00 mm by 160 mm, Dome" in row.toolTip()
    assert cylinder_tab.ui.label_template_status.text() == "Saved Standard 30"


def test_every_setting_on_the_tab_is_saved_in_its_own_field(cylinder_tab: CylinderView) -> None:
    """Check that each of the 11 settings is saved from its own control, all set to different values.

    The tab is set to 31.25 by 173 mm, a 3 by 12 mm collar, the notch off at 90 degrees, 3.5 by
    2.5 by 15 mm, and a flat tip. Fails if any value is missing, left at its default, or read
    from the wrong control, such as the collar thickness saved as its height, which with the
    defaults (both 0) no other test would notice. A template that swaps two settings prints a
    different device from the one the physicist designed.
    """
    from settings.cylinder_templates import CylinderDesign, load_templates

    view = cylinder_tab
    view.ui.spinbox_diameter.setValue(31.25)
    view.ui.spinbox_length.setValue(173)
    view.ui.cb_add_base.setChecked(True)
    view.ui.spinbox_base_thickness.setValue(3)
    view.ui.spinbox_base_height.setValue(12)
    view.ui.spinbox_notch_angle.setValue(90.0)
    view.ui.spinbox_notch_width.setValue(3.5)
    view.ui.spinbox_notch_depth.setValue(2.5)
    view.ui.spinbox_notch_height.setValue(15)
    view.ui.cb_add_notch.setChecked(False)
    view.ui.combobox_tip.setCurrentText("Flat")

    save_as(view, "Flat collar")

    [saved] = load_templates(library_path())
    assert saved.design == CylinderDesign(31.25, 173.0, True, 3.0, 12.0, False, 90.0, 3.5, 2.5, 15.0, True)


def test_a_value_typed_in_centimetres_is_saved_in_millimetres(cylinder_tab: CylinderView) -> None:
    """Check that 3.125 cm by 17.3 cm, typed with Units set to cm, is saved as 31.25 by 173 mm.

    Fails if the displayed numbers are saved instead, which would store a cylinder ten times
    too small, and loading it would print the wrong device for the patient.
    """
    from settings.cylinder_templates import load_templates

    cylinder_tab.ui.combobox_units.setCurrentText("cm")
    cylinder_tab.ui.spinbox_diameter.setValue(3.125)
    cylinder_tab.ui.spinbox_length.setValue(17.3)

    save_as(cylinder_tab, "Typed in cm")

    [saved] = load_templates(library_path())
    assert (saved.design.diameter_mm, saved.design.length_mm) == (31.25, 173.0)


@pytest.mark.parametrize("name, reason", [
    ("   ", "A cylinder template needs a name"),
    ("STANDARD 30", "A cylinder template named STANDARD 30 already exists. Use Update to change it"),
])
def test_a_blank_or_taken_name_says_why_and_saves_nothing(cylinder_tab: CylinderView, name: str, reason: str) -> None:
    """Check that a blank name, or "STANDARD 30" next to "Standard 30", is refused in the status line.

    Fails if the list grows, the file changes, or the status line does not say why. A silent
    refusal would leave the physicist believing the template was saved.
    """
    save_as(cylinder_tab, "Standard 30")
    before = library_path().read_text(encoding="utf-8")

    save_as(cylinder_tab, name)

    assert cylinder_tab.ui.list_templates.count() == 1
    assert library_path().read_text(encoding="utf-8") == before
    assert cylinder_tab.ui.label_template_status.text() == reason


def test_an_unreadable_library_empties_the_list_and_names_the_file(cylinder_tab: CylinderView) -> None:
    """Check that a corrupt library file empties the list, names the file, and raises nothing.

    Fails if reading it raises, or the list still offers templates. The library is read when
    the window is built, so an exception would stop brachify starting, and startup failures
    only reach app.log.
    """
    save_as(cylinder_tab, "Standard 30")
    library_path().write_text("not json", encoding="utf-8")

    cylinder_tab.action_load_templates()

    assert cylinder_tab.ui.list_templates.count() == 0
    assert "cylinder_templates.json could not be read" in cylinder_tab.ui.label_template_status.text()


def test_the_template_ranges_match_the_cylinder_tabs_spin_boxes(cylinder_tab: CylinderView) -> None:
    """Check that every template range is the matching Cylinder tab spin box's range in mm.

    Fails if a spin box limit changes in cylinder_view.ui without RANGES, or the other way
    round. A template could then hold a value the box clamps silently on loading, or the tab
    could build a cylinder its template refuses. The diameter box allows 0, which builds
    nothing, so its template minimum is the box's smallest step, 0.01 mm.
    """
    from settings.cylinder_templates import RANGES

    view = cylinder_tab
    fields = {
        "length_mm": view.length_field, "collar_thickness_mm": view.base_thickness_field,
        "collar_height_mm": view.base_height_field, "notch_width_mm": view.notch_width_field,
        "notch_depth_mm": view.notch_depth_field, "notch_height_mm": view.notch_height_field,
    }
    for key, field in fields.items():
        assert (RANGES[key].minimum, RANGES[key].maximum) == (field.minimum_mm, field.maximum_mm), key
    angle = view.ui.spinbox_notch_angle
    assert (RANGES["notch_angle_deg"].minimum, RANGES["notch_angle_deg"].maximum) == (angle.minimum(), angle.maximum())
    assert (view.diameter_field.minimum_mm, view.diameter_field.maximum_mm) == (0.0, RANGES["diameter_mm"].maximum)
    assert RANGES["diameter_mm"].minimum == 0.01
