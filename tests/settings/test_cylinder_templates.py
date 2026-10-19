"""Exercise src/settings/cylinder_templates.py: cylinder templates and the checks on their values."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from settings.cylinder_templates import (
    CylinderDesign,
    CylinderTemplate,
    CylinderTemplateError,
    make_template,
)

SAVED_AT = datetime(2026, 10, 19, 17, 5, tzinfo=timezone.utc)
STANDARD = CylinderDesign(
    diameter_mm=30.0, length_mm=160.0,
    collar_enabled=False, collar_thickness_mm=0.0, collar_height_mm=0.0,
    notch_enabled=True, notch_angle_deg=0.0, notch_width_mm=2.0, notch_depth_mm=1.8,
    notch_height_mm=10.0, flat_tip=False,
)


def template_named(name: str, template_id: str = "a1", design: CylinderDesign = STANDARD) -> CylinderTemplate:
    """Build a valid template saved at SAVED_AT, as a helper and not a test.

    Fails with CylinderTemplateError only if make_template refuses a template the spec allows.
    """
    return make_template(template_id, name, "", design, SAVED_AT, SAVED_AT)


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
