"""Exercise src/settings/needle_templates.py: the needle template library on disk."""
import json
from pathlib import Path

import pytest

from settings.needle_templates import (
    NeedleTemplate,
    NeedleTemplateError,
    load_templates,
    make_template,
    save_template,
)

LibraryJson = list[dict[str, str | float]] | dict[str, str | float]


def test_a_saved_template_loads_back_with_identical_values(tmp_path: Path) -> None:
    """Check that a template written to the library reads back exactly as it was saved.

    Fails if the name or the diameter changes on the round trip, for example by rounding.
    This is FR-CN-05: a clinician applying "Plastic 6F" next week must get the same channel
    width they saved, or the needle will not fit the printed cylinder.
    """
    library = tmp_path / "needle_templates.json"

    save_template(library, make_template("Plastic 6F", 2.05))

    assert load_templates(library) == (NeedleTemplate("Plastic 6F", 2.05),)


def test_saving_under_an_existing_name_replaces_that_template(tmp_path: Path) -> None:
    """Check that a name stays unique, and the newest diameter wins.

    Fails if the library holds two "Metal" entries, or keeps the old 1.9 mm. Two templates
    with one name would leave the clinician guessing which width Apply Template uses.
    """
    library = tmp_path / "needle_templates.json"
    save_template(library, make_template("Metal", 1.9))

    save_template(library, make_template("Metal", 2.1))

    assert load_templates(library) == (NeedleTemplate("Metal", 2.1),)


def test_no_library_file_means_no_templates_yet(tmp_path: Path) -> None:
    """Check that a first run, before anything is saved, has an empty library.

    Fails if a missing file raises instead of returning no templates. Every new install
    starts without the file, and the Channels tab must still open.
    """
    assert load_templates(tmp_path / "needle_templates.json") == ()


@pytest.mark.parametrize("name", ["", "   "])
def test_a_template_without_a_name_is_rejected(name: str) -> None:
    """Check that an empty or blank name is refused with NeedleTemplateError.

    Fails if the template is created anyway. FR-CN-05 requires it, and an unnamed entry could
    not be told apart in the template list.
    """
    with pytest.raises(NeedleTemplateError):
        make_template(name, 2.0)


@pytest.mark.parametrize("diameter_mm", [0.2, float("nan")])
def test_a_diameter_below_the_minimum_or_not_a_number_is_rejected(diameter_mm: float) -> None:
    """Check that a template cannot hold a diameter channels are never built with.

    Fails if 0.2 mm or NaN is accepted. 0.2 mm would cut a hole no needle passes through, and
    a NaN diameter reaching the geometry crashes OpenCASCADE.
    """
    with pytest.raises(NeedleTemplateError):
        make_template("Too thin", diameter_mm)


def test_spaces_around_a_name_are_trimmed() -> None:
    """Check that "  Metal  " is saved as "Metal".

    Fails if the spaces are kept, which would let "Metal" and " Metal" coexist as two
    templates that look identical in the list.
    """
    assert make_template("  Metal  ", 1.9).name == "Metal"


def test_a_corrupt_library_is_reported_and_left_unchanged(tmp_path: Path) -> None:
    """Check that saving into an unreadable library raises and does not overwrite it.

    Fails if save_template succeeds or rewrites the file. FR-CN-06: a corrupted file must
    leave the library unchanged, because overwriting it would silently delete every template
    the clinic had saved.
    """
    library = tmp_path / "needle_templates.json"
    library.write_text("not json", encoding="utf-8")

    with pytest.raises(NeedleTemplateError):
        save_template(library, make_template("Plastic 6F", 2.0))

    assert library.read_text(encoding="utf-8") == "not json"


@pytest.mark.parametrize("entries", [
    [{"name": "No diameter"}],
    [{"diameter_mm": 2.0}],
    {"name": "Not a list", "diameter_mm": 2.0},
    [{"name": "Twice", "diameter_mm": 2.0}, {"name": "Twice", "diameter_mm": 2.5}],
])
def test_a_library_with_a_malformed_entry_is_rejected(tmp_path: Path, entries: LibraryJson) -> None:
    """Check that a hand-edited library missing a field, or naming a template twice, is refused.

    Fails if load_templates returns templates from it. A partly read library would show the
    clinician templates whose widths came from the wrong entry.
    """
    library = tmp_path / "needle_templates.json"
    library.write_text(json.dumps(entries), encoding="utf-8")

    with pytest.raises(NeedleTemplateError):
        load_templates(library)


def test_a_library_that_cannot_be_read_is_reported(tmp_path: Path) -> None:
    """Check that a library path the system cannot read raises NeedleTemplateError.

    A folder stands where the file should be, which raises IsADirectoryError on macOS and
    Linux and PermissionError on Windows, both OSError. Fails if the OSError escapes. The
    Channels tab will read the library while the window is being built, so an escaped error
    would stop brachify from starting, and the clinician would only find it in app.log.
    """
    library = tmp_path / "needle_templates.json"
    library.mkdir()

    with pytest.raises(NeedleTemplateError):
        load_templates(library)


def test_a_library_that_cannot_be_written_is_reported(tmp_path: Path) -> None:
    """Check that a library the system cannot write raises NeedleTemplateError.

    A file stands where the library's folder should be, so creating the folder raises an
    OSError. Fails if that OSError escapes. Save as Template will show NeedleTemplateError in
    its status line, so any other error would leave the clinician believing the template was
    saved.
    """
    not_a_folder = tmp_path / "brachify"
    not_a_folder.write_text("a file where the folder should be", encoding="utf-8")

    with pytest.raises(NeedleTemplateError):
        save_template(not_a_folder / "needle_templates.json", make_template("Metal", 1.9))
