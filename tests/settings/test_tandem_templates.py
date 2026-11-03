"""Exercise src/settings/tandem_templates.py: tandem templates and their checks."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from settings.tandem_templates import TandemDesign, TandemTemplateError, make_template

SAVED_AT = datetime(2026, 11, 2, 17, 5, tzinfo=timezone.utc)
STANDARD = TandemDesign(
    height_mm=120.0, channel_diameter_mm=3.8, stopper_diameter_mm=5.0, bend_angle_deg=30.0,
    bend_radius_mm=35.0, threading_depth_mm=7.0, threading_diameter_mm=5.0, rotation_deg=0.0,
)


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
