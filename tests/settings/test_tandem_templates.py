"""Exercise src/settings/tandem_templates.py: tandem templates, their checks, and the library on disk."""
import json
import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from settings.tandem_templates import (
    TandemDesign,
    TandemTemplate,
    TandemTemplateError,
    add_template,
    load_templates,
    make_template,
)

SAVED_AT = datetime(2026, 11, 2, 17, 5, tzinfo=timezone.utc)
STANDARD = TandemDesign(
    height_mm=120.0, channel_diameter_mm=3.8, stopper_diameter_mm=5.0, bend_angle_deg=30.0,
    bend_radius_mm=35.0, threading_depth_mm=7.0, threading_diameter_mm=5.0, rotation_deg=0.0,
)
STANDARD_JSON = {
    "id": "a1", "name": "Standard", "note": "", "created": SAVED_AT.isoformat(), "modified": SAVED_AT.isoformat(),
    "height_mm": 120.0, "channel_diameter_mm": 3.8, "stopper_diameter_mm": 5.0, "bend_angle_deg": 30.0,
    "bend_radius_mm": 35.0, "threading_depth_mm": 7.0, "threading_diameter_mm": 5.0, "rotation_deg": 0.0,
}

JsonScalar = str | float | bool | None
LibraryJson = dict[str, int | str | list[dict[str, JsonScalar]]] | list[dict[str, JsonScalar]]


def template_named(name: str, template_id: str = "a1", design: TandemDesign = STANDARD) -> TandemTemplate:
    """Build a valid template saved at SAVED_AT, as a helper and not a test.

    Fails with TandemTemplateError only if make_template refuses a template the spec allows.
    """
    return make_template(template_id, name, "", design, SAVED_AT, SAVED_AT)


def write_library(path: Path, entries: LibraryJson) -> None:
    """Write a hand-made library file, as a clinician editing it by hand would, as a helper and not a test."""
    path.write_text(json.dumps(entries), encoding="utf-8")


def test_a_template_keeps_every_value_it_was_made_with() -> None:
    """Check that a template holds its ID, name, note, dates and all eight settings unchanged.

    Every setting differs from the Generate defaults, so a value dropped or swapped for another
    shows. Fails if make_template changes any of them. A clinician loading a template must get
    the tandem they saved, or the printed cylinder's tandem hole differs from the approved design.
    """
    design = TandemDesign(140.5, 4.2, 6.5, 45.0, 40.0, 8.0, 5.5, 258.697)

    template = make_template("b2", "Long bend", "For deep cases", design, SAVED_AT, SAVED_AT + timedelta(hours=1))

    assert (template.template_id, template.name, template.note) == ("b2", "Long bend", "For deep cases")
    assert (template.created, template.modified, template.design) == (SAVED_AT, SAVED_AT + timedelta(hours=1), design)


@pytest.mark.parametrize("name", ["", "   "])
def test_a_template_without_a_name_is_rejected(name: str) -> None:
    """Check that an empty or blank name is refused with TandemTemplateError.

    Fails if the template is made anyway. An unnamed entry cannot be told apart in the list.
    """
    with pytest.raises(TandemTemplateError, match="A tandem template needs a name"):
        make_template("a1", name, "", STANDARD, SAVED_AT, SAVED_AT)


def test_spaces_around_the_name_and_note_are_trimmed() -> None:
    """Check that "  Standard  " and "  note  " are kept as "Standard" and "note".

    Fails if the spaces are kept, which would let "Standard" and " Standard" look identical in
    the list while counting as different names.
    """
    template = make_template("a1", "  Standard  ", "  note  ", STANDARD, SAVED_AT, SAVED_AT)

    assert (template.name, template.note) == ("Standard", "note")


def test_a_template_without_an_id_is_rejected() -> None:
    """Check that an empty ID is refused with TandemTemplateError.

    Fails if the template is made. Update and Delete will find a template by its ID, so an entry
    without one could never be changed or removed from the Tandem tab.
    """
    with pytest.raises(TandemTemplateError, match="A tandem template needs an ID"):
        make_template("", "Standard", "", STANDARD, SAVED_AT, SAVED_AT)


@pytest.mark.parametrize("field, value, reason", [
    ("height_mm", 9.9, "Tandem Height must be from 10 to 500 mm"),
    ("height_mm", 500.1, "Tandem Height must be from 10 to 500 mm"),
    ("channel_diameter_mm", 0.4, "Channel Diameter must be from 0.5 to 99.99 mm"),
    ("stopper_diameter_mm", 100.0, "Stopper Diameter must be from 0.5 to 99.99 mm"),
    ("bend_angle_deg", -0.1, "Bend Angle must be from 0 to 99.99°"),
    ("bend_radius_mm", 9.9, "Bend Radius must be from 10 to 1000 mm"),
    ("threading_depth_mm", 350.1, "Threading Depth must be from 0 to 350 mm"),
    ("threading_diameter_mm", -0.1, "Threading Diameter must be from 0 to 350 mm"),
    ("rotation_deg", 360.1, "Rotation must be from -360 to 360°"),
    ("rotation_deg", float("nan"), "Rotation must be from -360 to 360°"),
    ("height_mm", float("inf"), "Tandem Height must be from 10 to 500 mm"),
])
def test_a_value_outside_the_generate_tabs_range_is_rejected(field: str, value: float, reason: str) -> None:
    """Check that each value just outside its Generate spin box range, NaN and infinity are refused, naming the setting.

    Fails if the template is made or the message names another setting or range. Loading an
    out-of-range value would be clamped silently by the spin box, so the tab would show, and
    Generate Tandem would build, a different tandem from the one saved. NaN reaching
    OpenCASCADE crashes brachify.
    """
    with pytest.raises(TandemTemplateError, match=reason):
        make_template("a1", "Out of range", "", replace(STANDARD, **{field: value}), SAVED_AT, SAVED_AT)


def test_a_value_on_the_edge_of_its_range_is_accepted() -> None:
    """Check that the smallest and largest values the Generate spin boxes allow are accepted.

    Fails if a range check is off by one step, which would refuse a tandem the tab can build.
    """
    smallest = TandemDesign(10.0, 0.5, 0.5, 0.0, 10.0, 0.0, 0.0, -360.0)
    largest = TandemDesign(500.0, 99.99, 99.99, 99.99, 1000.0, 350.0, 350.0, 360.0)

    assert make_template("a1", "Small", "", smallest, SAVED_AT, SAVED_AT).design == smallest
    assert make_template("a2", "Large", "", largest, SAVED_AT, SAVED_AT).design == largest


def test_a_time_without_a_time_zone_or_modified_before_created_is_rejected() -> None:
    """Check that a naive timestamp, or one modified before it was created, is refused.

    Fails if either template is made. A time with no zone reads differently on two machines,
    and a modified date before the created date means the entry was edited by hand wrongly.
    """
    with pytest.raises(TandemTemplateError, match="need a time zone"):
        make_template("a1", "Naive", "", STANDARD, datetime(2026, 11, 2), datetime(2026, 11, 2))
    with pytest.raises(TandemTemplateError, match="cannot be modified before"):
        make_template("a1", "Backwards", "", STANDARD, SAVED_AT, SAVED_AT - timedelta(seconds=1))


def test_a_saved_template_loads_back_with_identical_values(tmp_path: Path) -> None:
    """Check that a template written to the library reads back exactly as it was saved.

    Every setting differs from the Generate defaults, and the rotation is a plan's 258.697
    degrees. Fails if any value, the note or a timestamp changes on the round trip. FR-CN-05: a
    clinician loading a template must get the tandem they saved.
    """
    library = tmp_path / "tandem_templates.json"
    design = TandemDesign(140.5, 4.2, 6.5, 45.0, 40.0, 8.0, 5.5, 258.697)
    saved = make_template("b2", "Long bend", "For deep cases", design, SAVED_AT, SAVED_AT + timedelta(hours=1))

    add_template(library, saved)

    assert load_templates(library) == (saved,)


def test_no_library_file_means_no_templates_yet(tmp_path: Path) -> None:
    """Check that a first run, before anything is saved, has an empty library.

    Fails if a missing file raises. Every install starts without the file, and the Tandem tab
    must still open.
    """
    assert load_templates(tmp_path / "tandem_templates.json") == ()


def test_a_name_already_used_in_any_case_is_refused_and_the_file_kept(tmp_path: Path) -> None:
    """Check that saving "STANDARD" next to "Standard" raises and leaves the library as it was.

    Fails if the second template is added, or the file changes. Two names differing only in
    case read as the same template, so the clinician could load the wrong tandem. The message
    points to Update, which is how an existing template is changed.
    """
    library = tmp_path / "tandem_templates.json"
    add_template(library, template_named("Standard"))
    before = library.read_text(encoding="utf-8")

    with pytest.raises(TandemTemplateError, match="A tandem template named STANDARD already exists. Use Update"):
        add_template(library, template_named("STANDARD", template_id="b2"))

    assert library.read_text(encoding="utf-8") == before


def test_a_template_with_an_id_already_saved_is_refused(tmp_path: Path) -> None:
    """Check that a second template reusing a saved ID raises and leaves the library as it was.

    Fails if it is added. Update and Delete find a template by its ID, so two sharing one would
    let a change meant for one template land on the other.
    """
    library = tmp_path / "tandem_templates.json"
    add_template(library, template_named("Standard"))
    before = library.read_text(encoding="utf-8")

    with pytest.raises(TandemTemplateError, match="with this ID already exists"):
        add_template(library, template_named("Other"))

    assert library.read_text(encoding="utf-8") == before


@pytest.mark.parametrize("entries", [
    {"version": 2, "templates": [STANDARD_JSON]},
    {"version": 1, "templates": STANDARD_JSON},
    [STANDARD_JSON],
    {"version": 1, "templates": [{key: value for key, value in STANDARD_JSON.items() if key != "rotation_deg"}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "threading_depth_mm": True}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "height_mm": "120"}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "height_mm": 9.0}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "id": ""}]},
    {"version": 1, "templates": [{**STANDARD_JSON, "created": "yesterday"}]},
    {"version": 1, "templates": [STANDARD_JSON, {**STANDARD_JSON, "name": "Other"}]},
    {"version": 1, "templates": [STANDARD_JSON, {**STANDARD_JSON, "id": "b2", "name": "STANDARD"}]},
])
def test_a_library_with_a_malformed_entry_is_rejected(tmp_path: Path, entries: LibraryJson) -> None:
    """Check that a hand-edited library with a wrong version, shape, type, value, ID or name is refused whole.

    Covers version 2, templates not a list, a bare list, a missing rotation, true or text as a
    number, a height below the Generate range, an empty ID, an unreadable date, two templates
    sharing an ID, and two names differing only in case. Fails if load_templates returns
    templates from any of them. true is put in Threading Depth, whose range includes 1, so only
    the type check refuses it: read as a number it would cut a 1 mm thread nobody chose.
    """
    library = tmp_path / "tandem_templates.json"
    write_library(library, entries)

    with pytest.raises(TandemTemplateError, match="tandem_templates.json could not be read"):
        load_templates(library)


def test_a_number_too_large_for_a_float_is_reported_not_raised(tmp_path: Path) -> None:
    """Check that a JSON height of 10 to the 400 raises TandemTemplateError, not OverflowError.

    Fails if OverflowError escapes. The Tandem tab will handle only TandemTemplateError, so an
    escaped error would stop brachify starting over one hand-edited number.
    """
    library = tmp_path / "tandem_templates.json"
    entry = json.dumps({**STANDARD_JSON, "height_mm": 0}).replace('"height_mm": 0', '"height_mm": 1' + "0" * 400)
    library.write_text('{"version": 1, "templates": [' + entry + "]}", encoding="utf-8")

    with pytest.raises(TandemTemplateError):
        load_templates(library)


def test_a_corrupt_library_is_reported_and_left_unchanged(tmp_path: Path) -> None:
    """Check that adding to an unreadable library raises and does not overwrite it.

    Fails if add_template succeeds or rewrites the file. Overwriting it would silently delete
    every tandem template the clinic had saved.
    """
    library = tmp_path / "tandem_templates.json"
    library.write_text("not json", encoding="utf-8")

    with pytest.raises(TandemTemplateError):
        add_template(library, template_named("Standard"))

    assert library.read_text(encoding="utf-8") == "not json"


def test_a_library_that_cannot_be_read_is_reported(tmp_path: Path) -> None:
    """Check that a folder standing where the library should be raises TandemTemplateError.

    That raises IsADirectoryError on macOS and Linux and PermissionError on Windows, both
    OSError. Fails if the OSError escapes, which would stop the Tandem tab being built.
    """
    library = tmp_path / "tandem_templates.json"
    library.mkdir()

    with pytest.raises(TandemTemplateError):
        load_templates(library)


def test_a_library_that_cannot_be_written_is_reported(tmp_path: Path) -> None:
    """Check that a file standing where the library's folder should be raises TandemTemplateError.

    Fails if the OSError escapes. Save as Template will show TandemTemplateError in its status
    line, so any other error would leave the clinician believing the template was saved.
    """
    not_a_folder = tmp_path / "brachify"
    not_a_folder.write_text("a file where the folder should be", encoding="utf-8")

    with pytest.raises(TandemTemplateError, match="tandem_templates.json could not be saved"):
        add_template(not_a_folder / "tandem_templates.json", template_named("Standard"))


def test_a_failed_save_keeps_the_previous_library_and_leaves_no_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check that a save failing while the file is replaced leaves the old library whole.

    os.replace is made to fail, as a full disk or a locked file would. Fails if the saved
    template is lost, if TandemTemplateError is not raised, or if a temporary file stays.
    Writing the library in place would leave truncated JSON, and the next start would refuse
    every template the clinic had saved.
    """
    library = tmp_path / "tandem_templates.json"
    add_template(library, template_named("Standard"))
    before = library.read_text(encoding="utf-8")

    def refuse_to_replace(source: Path, destination: Path) -> None:
        """Stand in for os.replace failing, as a helper and not a test."""
        raise OSError("disk full")

    with monkeypatch.context() as patch:
        patch.setattr(os, "replace", refuse_to_replace)
        with pytest.raises(TandemTemplateError):
            add_template(library, template_named("Long", template_id="b2"))

    assert library.read_text(encoding="utf-8") == before
    assert list(tmp_path.iterdir()) == [library]
