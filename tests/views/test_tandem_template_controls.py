"""Exercise the tandem template controls in the Tandem tab's Generate sub-tab."""
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
    from windows.views.tandem_view import TandemView

TANDEM_TAB = 3


def click(button: QPushButton) -> None:
    """Click a button with the left mouse button, the way a clinician does.

    A helper, not a test. QTest sends a real press and release, so every slot the view
    connected to the button runs, and a disabled button ignores the click.
    """
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)


def library_path() -> Path:
    """Return the tandem template library inside this run's temporary home folder.

    A helper, not a test. units_app points HOME at a temporary folder before brachify is
    imported, so this never touches the developer's own ~/brachify.
    """
    from classes.info import USER_PATH
    from settings.tandem_templates import LIBRARY_FILE_NAME

    return USER_PATH / LIBRARY_FILE_NAME


@pytest.fixture
def tandem_tab(cylinder_window: MainWindow) -> Iterator[TandemView]:
    """Give each test the real Tandem tab, with no plan and an empty template library.

    A fixture, not a test. The library file outlives a window, so it is deleted before and
    after each test, and the tab rereads it, so no test sees another test's templates.
    """
    library_path().unlink(missing_ok=True)
    view = cylinder_window.navigationmodel.views[TANDEM_TAB]
    view.action_load_templates()
    yield view
    library_path().unlink(missing_ok=True)


def save_as(view: TandemView, name: str, note: str = "") -> None:
    """Type a name and a note and press Save as Template, as a helper and not a test."""
    view.ui.le_template_name.setText(name)
    view.ui.le_template_note.setText(note)
    click(view.ui.btn_save_template)


def test_save_as_template_lists_the_template_and_writes_it(tandem_tab: TandemView) -> None:
    """Check that Save as Template adds the Generate settings to the list and to the library file.

    The tab shows the default tandem. Fails if "Standard" is not listed, the file does not hold
    the eight default settings with its name and note, the row's tooltip does not summarise it,
    or the status line does not confirm the save. A template that is only listed is lost when
    brachify closes, and FR-CN-05 asks for one the clinician can use later.
    """
    from settings.tandem_templates import TandemDesign, load_templates

    save_as(tandem_tab, "Standard", "Clinic default")

    [saved] = load_templates(library_path())
    assert (saved.name, saved.note) == ("Standard", "Clinic default")
    assert saved.design == TandemDesign(170.0, 3.8, 5.0, 30.0, 35.0, 7.0, 5.0, 0.0)
    row = tandem_tab.ui.list_templates.item(0)
    assert row.text() == "Standard"
    assert "Clinic default" in row.toolTip() and "170 mm high, 30° bend, rotated 0°" in row.toolTip()
    assert tandem_tab.ui.label_template_status.text() == "Saved Standard"


def test_every_generate_setting_is_saved_from_its_own_box(tandem_tab: TandemView) -> None:
    """Check that each of the eight settings is saved from its own spin box, all set to different values.

    Fails if any value is missing, left at its default, or read from the wrong box, such as the
    threading depth saved as its diameter, or the rotation read from the Import sub-tab's box.
    A template that swaps two settings cuts a different tandem hole from the one designed.
    """
    from settings.tandem_templates import TandemDesign, load_templates

    ui = tandem_tab.ui
    ui.sb_tandem_height.setValue(140.5)
    ui.sp_channel_diameter.setValue(4.2)
    ui.sp_stopper_diameter.setValue(6.5)
    ui.sp_bend_angle.setValue(45.0)
    ui.sb_bend_radius.setValue(40.0)
    ui.sb_threading_depth.setValue(8.0)
    ui.sb_threading_diameter.setValue(5.5)
    ui.tandem_rotation_2.setValue(258.697)
    ui.tandem_rotation.setValue(12.0)

    save_as(tandem_tab, "Long bend")

    [saved] = load_templates(library_path())
    assert saved.design == TandemDesign(140.5, 4.2, 6.5, 45.0, 40.0, 8.0, 5.5, 258.697)


@pytest.mark.parametrize("name, reason", [
    ("   ", "A tandem template needs a name"),
    ("STANDARD", "A tandem template named STANDARD already exists. Use Update to change it"),
])
def test_a_blank_or_taken_name_says_why_and_saves_nothing(tandem_tab: TandemView, name: str, reason: str) -> None:
    """Check that a blank name, or "STANDARD" next to "Standard", is refused in the status line.

    Fails if the list grows, the file changes, or the status line does not say why. A silent
    refusal would leave the clinician believing the template was saved.
    """
    save_as(tandem_tab, "Standard")
    before = library_path().read_text(encoding="utf-8")

    save_as(tandem_tab, name)

    assert tandem_tab.ui.list_templates.count() == 1
    assert library_path().read_text(encoding="utf-8") == before
    assert tandem_tab.ui.label_template_status.text() == reason


def test_an_unreadable_library_empties_the_list_and_names_the_file(tandem_tab: TandemView) -> None:
    """Check that a corrupt library file empties the list, names the file, and raises nothing.

    Fails if reading it raises, or the list still offers templates. The library is read when
    the window is built, so an exception would stop brachify starting, and startup failures
    only reach app.log.
    """
    save_as(tandem_tab, "Standard")
    library_path().write_text("not json", encoding="utf-8")

    tandem_tab.action_load_templates()

    assert tandem_tab.ui.list_templates.count() == 0
    assert "tandem_templates.json could not be read" in tandem_tab.ui.label_template_status.text()


def test_the_template_ranges_match_the_generate_spin_boxes(tandem_tab: TandemView) -> None:
    """Check that every template range is the matching Generate spin box's range.

    Fails if a spin box limit changes in tandem_view.ui without RANGES, or the other way round.
    A template could then hold a value the box clamps silently on loading, or the tab could
    build a tandem its template refuses. The Tandem Height box is checked before any plan, so
    its maximum is still the .ui's 500 mm rather than a cylinder's length.
    """
    from settings.tandem_templates import RANGES

    ui = tandem_tab.ui
    boxes = {
        "height_mm": ui.sb_tandem_height, "channel_diameter_mm": ui.sp_channel_diameter,
        "stopper_diameter_mm": ui.sp_stopper_diameter, "bend_angle_deg": ui.sp_bend_angle,
        "bend_radius_mm": ui.sb_bend_radius, "threading_depth_mm": ui.sb_threading_depth,
        "threading_diameter_mm": ui.sb_threading_diameter, "rotation_deg": ui.tandem_rotation_2,
    }
    for key, box in boxes.items():
        assert (RANGES[key].minimum, RANGES[key].maximum) == (box.minimum(), box.maximum()), key
