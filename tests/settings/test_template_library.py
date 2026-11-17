"""Exercise src/settings/template_library.py: the rules every template library shares, on two made-up kinds."""
import os
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from settings.template_library import (
    JsonValue, Range, TemplateLibrary, TemplateLibraryError, decode_number, decode_time,
)

SAVED_AT = datetime(2026, 11, 17, 9, 30, tzinfo=timezone.utc)
LATER = SAVED_AT + timedelta(days=2)
SIZE = {"size_mm": Range("Widget Size", 1.0, 50.0, " mm")}


class WidgetError(TemplateLibraryError):
    """The error the made-up widget kind raises, as CylinderTemplateError does for cylinders."""


class GadgetError(TemplateLibraryError):
    """The error a second made-up kind raises, so a message's noun can be checked per kind."""


@dataclass(frozen=True)
class Widget:
    template_id: str
    name: str
    created: datetime
    modified: datetime
    size_mm: float


def decode_widget(entry: JsonValue) -> Widget:
    """Turn one JSON entry into a Widget, as a real kind's decode_template does. A helper, not a test."""
    match entry:
        case {"id": str(template_id), "name": str(name), "created": str(created), "modified": str(modified)}:
            return Widget(template_id, name, decode_time(created), decode_time(modified),
                          decode_number(entry.get("size_mm"), "size_mm"))
    raise WidgetError("an entry is not a widget template")


def encode_widget(widget: Widget) -> dict[str, JsonValue]:
    """Turn a Widget into its JSON entry, as a real kind's encode_template does. A helper, not a test."""
    return {"id": widget.template_id, "name": widget.name, "created": widget.created.isoformat(),
            "modified": widget.modified.isoformat(), "size_mm": widget.size_mm}


WIDGETS = TemplateLibrary("widget", WidgetError, 1, decode_widget, encode_widget)
GADGETS = TemplateLibrary("gadget", GadgetError, 1, decode_widget, encode_widget)


def saved_library(path: Path, *names: str) -> tuple[Widget, ...]:
    """Save one widget per name, with IDs a1, a2 and so on, and return the library. A helper, not a test."""
    templates: tuple[Widget, ...] = ()
    for number, name in enumerate(names, start=1):
        templates = WIDGETS.add(path, Widget(f"a{number}", name, SAVED_AT, SAVED_AT, 10.0))
    return templates


def test_a_saved_template_loads_back_identical_and_no_file_means_no_templates(tmp_path: Path) -> None:
    """Check that add then load returns the templates unchanged in order, and a missing file is empty.

    Fails if a field changes in the JSON file, or loading raises or creates the file. A template that
    changed in storage would put different numbers in a clinician's design.
    """
    path = tmp_path / "widgets.json"
    assert WIDGETS.load(path) == () and not path.exists()

    saved = saved_library(path, "Standard", "Long")

    assert WIDGETS.load(path) == saved
    assert [widget.name for widget in saved] == ["Standard", "Long"]


def test_a_repeated_name_or_id_is_refused_naming_the_kind_and_the_file_is_kept(tmp_path: Path) -> None:
    """Check that add refuses a name in another case and an ID already saved, each kind naming itself.

    Fails if a duplicate is saved or a message says widget for a gadget. Lookalike names could not be
    told apart in the tab, and a message naming the wrong kind is the copy-paste bug this ends.
    """
    path = tmp_path / "widgets.json"
    saved_library(path, "Standard")
    before = path.read_text(encoding="utf-8")

    with pytest.raises(WidgetError, match="A widget template named STANDARD already exists. Use Update"):
        WIDGETS.add(path, Widget("b2", "STANDARD", SAVED_AT, SAVED_AT, 10.0))
    with pytest.raises(WidgetError, match="A widget template with this ID already exists"):
        WIDGETS.add(path, Widget("a1", "Other", SAVED_AT, SAVED_AT, 10.0))
    with pytest.raises(GadgetError, match="That gadget template no longer exists"):
        GADGETS.delete(path, "missing")

    assert path.read_text(encoding="utf-8") == before


@pytest.mark.parametrize("text", ['{"version": 2, "templates": []}', '{"version": 1, "templates": [{"id": "a1"}]}', "not json"])
def test_a_foreign_or_corrupt_library_is_reported_naming_the_file_and_left_unchanged(tmp_path: Path, text: str) -> None:
    """Check that another version, a bad entry and malformed JSON raise WidgetError naming the file, even from update.

    Fails if the file loads or an update overwrites it. A hand-edited file must be reported for repair,
    never replaced by an empty library.
    """
    path = tmp_path / "widgets.json"
    path.write_text(text, encoding="utf-8")

    with pytest.raises(WidgetError, match="widgets.json could not be read"):
        WIDGETS.load(path)
    with pytest.raises(WidgetError, match="widgets.json could not be read"):
        WIDGETS.update(path, "a1", lambda old: old)

    assert path.read_text(encoding="utf-8") == text


def test_a_failed_save_keeps_the_previous_library_and_leaves_no_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check that a save failing while the file is replaced leaves the old library whole.

    os.replace is made to fail, as a full disk would. Fails if the saved template is lost or a .tmp file
    stays. Writing in place would leave truncated JSON, and the next start would refuse every template.
    """
    path = tmp_path / "widgets.json"
    saved_library(path, "Standard")
    before = path.read_text(encoding="utf-8")

    def refuse_to_replace(source: Path, destination: Path) -> None:
        """Stand in for os.replace failing, as a helper and not a test."""
        raise OSError("disk full")

    with monkeypatch.context() as patch:
        patch.setattr(os, "replace", refuse_to_replace)
        with pytest.raises(WidgetError, match="widgets.json could not be saved"):
            WIDGETS.add(path, Widget("b2", "Long", SAVED_AT, SAVED_AT, 10.0))

    assert path.read_text(encoding="utf-8") == before
    assert list(tmp_path.iterdir()) == [path]


def test_updating_keeps_the_place_and_refuses_another_templates_name_but_not_a_recased_own(tmp_path: Path) -> None:
    """Check that update puts revise's result in the old slot, refuses a name another template holds, allows a recase.

    Fails if the list is reordered, the clash is saved, or renaming First to FIRST is refused. A template
    that jumped position would be selected by mistake.
    """
    path = tmp_path / "widgets.json"
    saved_library(path, "First", "Second", "Third")

    with pytest.raises(WidgetError, match="A widget template named FIRST already exists"):
        WIDGETS.update(path, "a2", lambda old: replace(old, name="FIRST"))
    updated = WIDGETS.update(path, "a1", lambda old: replace(old, name="FIRST", modified=LATER))

    assert [(widget.template_id, widget.name) for widget in updated] == [("a1", "FIRST"), ("a2", "Second"), ("a3", "Third")]
    assert (updated[0].created, updated[0].modified) == (SAVED_AT, LATER)


def test_deleting_removes_only_that_template_and_an_unknown_id_is_refused(tmp_path: Path) -> None:
    """Check that delete drops one template and keeps the rest in order, and an unknown ID raises.

    Fails if a neighbour goes with it or an unknown ID is accepted. Deleting the wrong template would lose a
    design saved for a patient.
    """
    path = tmp_path / "widgets.json"
    saved_library(path, "First", "Second", "Third")

    with pytest.raises(WidgetError, match="That widget template no longer exists"):
        WIDGETS.delete(path, "missing")
    remaining = WIDGETS.delete(path, "a2")

    assert [widget.name for widget in remaining] == ["First", "Third"]
    assert WIDGETS.load(path) == remaining


def test_a_name_is_trimmed_and_a_missing_name_or_id_or_bad_date_is_refused() -> None:
    """Check validated_name returns the trimmed name and refuses no name, no ID, a naive time, modified before created.

    Fails if a rule is dropped. A nameless template could not be told from another, and a time with no
    zone cannot be compared with one that has it.
    """
    assert WIDGETS.validated_name("a1", "  Standard  ", SAVED_AT, SAVED_AT) == "Standard"
    with pytest.raises(WidgetError, match="A widget template needs a name"):
        WIDGETS.validated_name("a1", "   ", SAVED_AT, SAVED_AT)
    with pytest.raises(WidgetError, match="A widget template needs an ID"):
        WIDGETS.validated_name("", "Standard", SAVED_AT, SAVED_AT)
    with pytest.raises(WidgetError, match="dates need a time zone"):
        WIDGETS.validated_name("a1", "Standard", SAVED_AT.replace(tzinfo=None), SAVED_AT)
    with pytest.raises(WidgetError, match="cannot be modified before it was created"):
        WIDGETS.validated_name("a1", "Standard", LATER, SAVED_AT)


@pytest.mark.parametrize("value", [0.99, 50.01, float("nan"), float("inf")])
def test_a_value_outside_its_range_is_refused_and_both_edges_are_allowed(value: float) -> None:
    """Check that check_ranges refuses a value just outside its limits, NaN and infinity included, and allows both edges.

    Fails if NaN passes or an edge is refused. A NaN would reach the geometry kernel and build a broken shape.
    """
    WIDGETS.check_ranges({"size_mm": 1.0}, SIZE)
    WIDGETS.check_ranges({"size_mm": 50.0}, SIZE)

    with pytest.raises(WidgetError, match="Widget Size must be from 1 to 50 mm"):
        WIDGETS.check_ranges({"size_mm": value}, SIZE)

