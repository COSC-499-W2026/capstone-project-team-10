"""Exercise src/settings/cylinder_templates.py: cylinder templates, their checks, and the library on disk."""
import json
import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from settings.cylinder_templates import (
    CylinderDesign,
    CylinderTemplate,
    CylinderTemplateError,
    add_template,
    delete_template,
    load_templates,
    make_template,
    update_template,
)

SAVED_AT = datetime(2026, 10, 19, 17, 5, tzinfo=timezone.utc)
STANDARD = CylinderDesign(
    diameter_mm=30.0, length_mm=160.0,
    collar_enabled=False, collar_thickness_mm=0.0, collar_height_mm=0.0,
    notch_enabled=True, notch_angle_deg=0.0, notch_width_mm=2.0, notch_depth_mm=1.8,
    notch_height_mm=10.0, flat_tip=False,
)
STANDARD_JSON = {
    "id": "a1", "name": "30 mm standard", "note": "", "created": SAVED_AT.isoformat(),
    "modified": SAVED_AT.isoformat(), "diameter_mm": 30.0, "length_mm": 160.0,
    "collar_enabled": False, "collar_thickness_mm": 0.0, "collar_height_mm": 0.0,
    "notch_enabled": True, "notch_angle_deg": 0.0, "notch_width_mm": 2.0, "notch_depth_mm": 1.8,
    "notch_height_mm": 10.0, "flat_tip": False,
}

JsonScalar = str | float | bool | None
LibraryJson = dict[str, int | str | list[dict[str, JsonScalar]]] | list[dict[str, JsonScalar]]


def template_named(name: str, template_id: str = "a1", design: CylinderDesign = STANDARD) -> CylinderTemplate:
    """Build a valid template saved at SAVED_AT, as a helper and not a test.

    Fails with CylinderTemplateError only if make_template refuses a template the spec allows.
    """
    return make_template(template_id, name, "", design, SAVED_AT, SAVED_AT)


def write_library(path: Path, entries: LibraryJson) -> None:
    """Write a hand-made library file, as a clinician editing it by hand would, as a helper and not a test."""
    path.write_text(json.dumps(entries), encoding="utf-8")


def test_a_saved_template_loads_back_with_identical_values(tmp_path: Path) -> None:
    """Check that a template written to the library reads back exactly as it was saved.

    The design is a flat 31.25 mm cylinder with a 3 by 12 mm collar and a notch at 90 degrees,
    so every field differs from its default. Fails if any value, the note or a timestamp
    changes on the round trip. FR-CN-05: a physicist loading a template must get the cylinder
    they saved, or the printed device differs from the approved design.
    """
    library = tmp_path / "cylinder_templates.json"
    design = CylinderDesign(
        diameter_mm=31.25, length_mm=173.0,
        collar_enabled=True, collar_thickness_mm=3.0, collar_height_mm=12.0,
        notch_enabled=False, notch_angle_deg=90.0, notch_width_mm=3.5, notch_depth_mm=2.5,
        notch_height_mm=15.0, flat_tip=True,
    )
    saved = make_template("b2", "Flat collar", "For long cases", design, SAVED_AT, SAVED_AT + timedelta(hours=1))

    add_template(library, saved)

    assert load_templates(library) == (saved,)


def test_no_library_file_means_no_templates_yet(tmp_path: Path) -> None:
    """Check that a first run, before anything is saved, has an empty library.

    Fails if a missing file raises. Every install starts without the file, and the Cylinder
    tab must still open.
    """
    assert load_templates(tmp_path / "cylinder_templates.json") == ()


@pytest.mark.parametrize("name", ["", "   "])
def test_a_template_without_a_name_is_rejected(name: str) -> None:
    """Check that an empty or blank name is refused with CylinderTemplateError.

    Fails if the template is made anyway. An unnamed entry cannot be told apart in the list,
    and FR-CN-05 asks for an empty name to be rejected.
    """
    with pytest.raises(CylinderTemplateError, match="needs a name"):
        template_named(name)


def test_spaces_around_the_name_and_note_are_trimmed() -> None:
    """Check that "  Standard  " and "  note  " are kept as "Standard" and "note".

    Fails if the spaces are kept, which would let "Standard" and " Standard" look identical in
    the list while counting as different names.
    """
    template = make_template("a1", "  Standard  ", "  note  ", STANDARD, SAVED_AT, SAVED_AT)

    assert (template.name, template.note) == ("Standard", "note")


def test_a_template_without_an_id_is_rejected() -> None:
    """Check that an empty ID is refused with CylinderTemplateError.

    Fails if the template is made. Update and Delete find a template by its ID, so an entry
    without one could never be changed or removed from the Cylinder tab.
    """
    with pytest.raises(CylinderTemplateError, match="needs an ID"):
        make_template("", "Standard", "", STANDARD, SAVED_AT, SAVED_AT)


def test_a_name_already_used_in_any_case_is_refused_and_the_file_kept(tmp_path: Path) -> None:
    """Check that saving "STANDARD" next to "Standard" raises and leaves the library as it was.

    Fails if the second template is added, or the file changes. Two names differing only in
    case read as the same template, so the physicist could load the wrong cylinder. The
    message points to Update, which is how an existing template is changed.
    """
    library = tmp_path / "cylinder_templates.json"
    add_template(library, template_named("Standard"))
    before = library.read_text(encoding="utf-8")

    with pytest.raises(CylinderTemplateError, match="already exists. Use Update"):
        add_template(library, template_named("STANDARD", template_id="b2"))

    assert library.read_text(encoding="utf-8") == before


@pytest.mark.parametrize("field, value", [
    ("diameter_mm", 0.0),
    ("diameter_mm", 100.0),
    ("length_mm", 59.0),
    ("length_mm", 301.0),
    ("collar_thickness_mm", -1.0),
    ("collar_height_mm", 99.5),
    ("notch_angle_deg", 360.0),
    ("notch_width_mm", 0.4),
    ("notch_depth_mm", 5.1),
    ("notch_height_mm", 61.0),
    ("length_mm", float("nan")),
    ("diameter_mm", float("inf")),
])
def test_a_value_outside_the_cylinder_tabs_range_is_rejected(field: str, value: float) -> None:
    """Check that each value just outside its Cylinder tab range, NaN and infinity are refused.

    The ranges are the tab's spin box limits in mm. Fails if the template is made. Loading an
    out-of-range value would be clamped silently by the spin box, so the tab would show, and
    Apply would build, a different cylinder from the one saved. A 0 mm diameter builds nothing
    printable, and NaN reaching OpenCASCADE crashes brachify.
    """
    with pytest.raises(CylinderTemplateError, match="must be from"):
        template_named("Out of range", design=replace(STANDARD, **{field: value}))


def test_a_value_on_the_edge_of_its_range_is_accepted() -> None:
    """Check that the smallest and largest values the Cylinder tab allows are accepted.

    Fails if a range check is off by one step, which would refuse a cylinder the tab can build.
    """
    smallest = CylinderDesign(0.01, 60.0, False, 0.0, 0.0, True, 0.0, 0.5, 0.5, 1.0, False)
    largest = CylinderDesign(99.99, 300.0, True, 99.0, 99.0, True, 359.9, 10.0, 5.0, 60.0, True)

    assert template_named("Small", design=smallest).design == smallest
    assert template_named("Large", design=largest).design == largest


def test_a_time_without_a_time_zone_or_modified_before_created_is_rejected() -> None:
    """Check that a naive timestamp, or one modified before it was created, is refused.

    Fails if either template is made. A time with no zone reads differently on two machines,
    and a modified date before the created date means the entry was edited by hand wrongly.
    """
    with pytest.raises(CylinderTemplateError):
        make_template("a1", "Naive", "", STANDARD, datetime(2026, 10, 19), datetime(2026, 10, 19))
    with pytest.raises(CylinderTemplateError):
        make_template("a1", "Backwards", "", STANDARD, SAVED_AT, SAVED_AT - timedelta(seconds=1))


@pytest.mark.parametrize("entries", [
    {"version": 2, "templates": [STANDARD_JSON]},
    {"version": 1, "templates": STANDARD_JSON},
    [STANDARD_JSON],
    {"version": 1, "templates": [{key: value for key, value in STANDARD_JSON.items() if key != "length_mm"}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "collar_thickness_mm": True}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "length_mm": "160"}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "flat_tip": 1}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "id": ""}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "created": "yesterday"}]},
    {"version": 1, "templates": [STANDARD_JSON, {**STANDARD_JSON, "name": "Other"}]},
    {"version": 1, "templates": [STANDARD_JSON, {**STANDARD_JSON, "id": "b2", "name": "30 MM STANDARD"}]},
])
def test_a_library_with_a_malformed_entry_is_rejected(tmp_path: Path, entries: LibraryJson) -> None:
    """Check that a hand-edited library with a wrong version, shape, type, ID or name is refused whole.

    Covers version 2, templates not a list, a bare list, a missing value, true or text as a
    number, 1 as a flag, an empty ID, an unreadable date, two templates sharing an ID, and two
    names differing only in case. Fails if load_templates returns templates from any of them.
    true is put in Collar Thickness, whose range includes 1, so only the type check refuses it:
    read as a number it would print a 1 mm collar nobody chose.
    """
    library = tmp_path / "cylinder_templates.json"
    write_library(library, entries)

    with pytest.raises(CylinderTemplateError, match="could not be read"):
        load_templates(library)


def test_a_number_too_large_for_a_float_is_reported_not_raised(tmp_path: Path) -> None:
    """Check that a JSON length of 10 to the 400 raises CylinderTemplateError, not OverflowError.

    Fails if OverflowError escapes. The Cylinder tab handles only CylinderTemplateError, so an
    escaped error would stop brachify starting over one hand-edited number.
    """
    library = tmp_path / "cylinder_templates.json"
    entry = json.dumps({**STANDARD_JSON, "length_mm": 0}).replace('"length_mm": 0', '"length_mm": 1' + "0" * 400)
    library.write_text('{"version": 1, "templates": [' + entry + "]}", encoding="utf-8")

    with pytest.raises(CylinderTemplateError):
        load_templates(library)


def test_a_corrupt_library_is_reported_and_left_unchanged(tmp_path: Path) -> None:
    """Check that adding to an unreadable library raises and does not overwrite it.

    Fails if add_template succeeds or rewrites the file. Overwriting it would silently delete
    every cylinder template the clinic had saved.
    """
    library = tmp_path / "cylinder_templates.json"
    library.write_text("not json", encoding="utf-8")

    with pytest.raises(CylinderTemplateError):
        add_template(library, template_named("Standard"))

    assert library.read_text(encoding="utf-8") == "not json"


def test_a_library_that_cannot_be_read_is_reported(tmp_path: Path) -> None:
    """Check that a folder standing where the library should be raises CylinderTemplateError.

    That raises IsADirectoryError on macOS and Linux and PermissionError on Windows, both
    OSError. Fails if the OSError escapes, which would stop the Cylinder tab being built.
    """
    library = tmp_path / "cylinder_templates.json"
    library.mkdir()

    with pytest.raises(CylinderTemplateError):
        load_templates(library)


def test_a_library_that_cannot_be_written_is_reported(tmp_path: Path) -> None:
    """Check that a file standing where the library's folder should be raises CylinderTemplateError.

    Fails if the OSError escapes. Save as Template shows CylinderTemplateError in its status
    line, so any other error would leave the physicist believing the template was saved.
    """
    not_a_folder = tmp_path / "brachify"
    not_a_folder.write_text("a file where the folder should be", encoding="utf-8")

    with pytest.raises(CylinderTemplateError):
        add_template(not_a_folder / "cylinder_templates.json", template_named("Standard"))


def test_a_failed_save_keeps_the_previous_library_and_leaves_no_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check that a save failing while the file is replaced leaves the old library whole.

    os.replace is made to fail, as a full disk or a locked file would. Fails if the saved
    template is lost, if CylinderTemplateError is not raised, or if a temporary file stays.
    Writing the library in place would leave truncated JSON, and the next start would refuse
    every template the clinic had saved.
    """
    library = tmp_path / "cylinder_templates.json"
    add_template(library, template_named("Standard"))
    before = library.read_text(encoding="utf-8")

    def refuse_to_replace(source: Path, destination: Path) -> None:
        """Stand in for os.replace failing, as a helper and not a test."""
        raise OSError("disk full")

    with monkeypatch.context() as patch:
        patch.setattr(os, "replace", refuse_to_replace)
        with pytest.raises(CylinderTemplateError):
            add_template(library, template_named("Long", template_id="b2"))

    assert library.read_text(encoding="utf-8") == before
    assert list(tmp_path.iterdir()) == [library]


LATER = SAVED_AT + timedelta(days=2)
LONG = replace(STANDARD, length_mm=180.0, flat_tip=True)


def library_of(path: Path, *names: str) -> tuple[CylinderTemplate, ...]:
    """Save one template per name, IDs "t0", "t1" and on, and return the library, as a helper and not a test."""
    for index, name in enumerate(names):
        add_template(path, template_named(name, template_id=f"t{index}"))
    return load_templates(path)


def test_updating_a_template_keeps_its_id_created_date_and_place(tmp_path: Path) -> None:
    """Check that Update replaces the name, note and settings but keeps the ID, created date and order.

    The middle of three templates is renamed, given a note and made 180 mm with a flat tip.
    Fails if the ID or created date changes, the modified date is not the update's, any of the
    new values is lost, or the template moves in the list. FR-CN-06: a physicist editing a
    template must find it where it was, as the same template.
    """
    library = tmp_path / "cylinder_templates.json"
    library_of(library, "Short", "Standard", "Wide")

    update_template(library, "t1", "Standard long", "Revised", LONG, LATER)

    assert load_templates(library)[1] == CylinderTemplate("t1", "Standard long", "Revised", SAVED_AT, LATER, LONG)
    assert [template.name for template in load_templates(library)] == ["Short", "Standard long", "Wide"]


def test_updating_to_another_templates_name_in_any_case_is_refused(tmp_path: Path) -> None:
    """Check that renaming "Standard" to "short" while "Short" exists raises and leaves the file alone.

    Fails if the rename is saved or the file changes. Two templates whose names differ only in
    case would read as one, so the physicist could load the wrong cylinder.
    """
    library = tmp_path / "cylinder_templates.json"
    library_of(library, "Short", "Standard")
    before = library.read_text(encoding="utf-8")

    with pytest.raises(CylinderTemplateError, match="already exists"):
        update_template(library, "t1", "short", "", STANDARD, LATER)

    assert library.read_text(encoding="utf-8") == before


def test_a_template_can_keep_its_own_name_in_another_case(tmp_path: Path) -> None:
    """Check that updating "Standard" to "STANDARD" is allowed, since no other template has that name.

    Fails if a template's own name counts as taken, which would stop the physicist changing the
    settings or the case of a name without renaming it to something else first.
    """
    library = tmp_path / "cylinder_templates.json"
    library_of(library, "Standard")

    update_template(library, "t0", "STANDARD", "", LONG, LATER)

    assert load_templates(library)[0].name == "STANDARD"


def test_an_update_with_a_value_outside_the_tabs_range_is_refused(tmp_path: Path) -> None:
    """Check that Update applies the same range checks as a new template, leaving the file alone.

    Fails if a 0 mm diameter is saved. An update must not slip past the checks that Save as
    Template applies, or a template could hold a cylinder the tab cannot show.
    """
    library = tmp_path / "cylinder_templates.json"
    library_of(library, "Standard")
    before = library.read_text(encoding="utf-8")

    with pytest.raises(CylinderTemplateError, match="must be from"):
        update_template(library, "t0", "Standard", "", replace(STANDARD, diameter_mm=0.0), LATER)

    assert library.read_text(encoding="utf-8") == before


def test_deleting_removes_only_that_template(tmp_path: Path) -> None:
    """Check that deleting the middle of three templates leaves the other two, in order.

    Fails if the wrong template, or more than one, is removed. Deleting is permanent, so the
    physicist must lose only the template they chose.
    """
    library = tmp_path / "cylinder_templates.json"
    short, _, wide = library_of(library, "Short", "Standard", "Wide")

    delete_template(library, "t1")

    assert load_templates(library) == (short, wide)


def test_an_unknown_template_cannot_be_updated_or_deleted(tmp_path: Path) -> None:
    """Check that Update and Delete of an ID not in the library raise and change nothing.

    Fails if either succeeds or changes the file. The template may have been deleted by
    another copy of brachify since the list was shown, and a silent success would tell the
    physicist a change was saved when it was not.
    """
    library = tmp_path / "cylinder_templates.json"
    library_of(library, "Standard")
    before = library.read_text(encoding="utf-8")

    with pytest.raises(CylinderTemplateError, match="no longer exists"):
        update_template(library, "gone", "Standard", "", STANDARD, LATER)
    with pytest.raises(CylinderTemplateError, match="no longer exists"):
        delete_template(library, "gone")

    assert library.read_text(encoding="utf-8") == before


def test_a_corrupt_library_is_not_changed_by_update_or_delete(tmp_path: Path) -> None:
    """Check that Update and Delete refuse an unreadable library and leave it as it was.

    Fails if either rewrites the file. Writing over it would silently delete every cylinder
    template the clinic had saved.
    """
    library = tmp_path / "cylinder_templates.json"
    library.write_text("not json", encoding="utf-8")

    with pytest.raises(CylinderTemplateError):
        update_template(library, "t0", "Standard", "", STANDARD, LATER)
    with pytest.raises(CylinderTemplateError):
        delete_template(library, "t0")

    assert library.read_text(encoding="utf-8") == "not json"
