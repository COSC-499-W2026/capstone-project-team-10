"""Exercise src/classes/pdf/template_reference.py: the numbers printed on the reference sheet."""
from __future__ import annotations

import pytest

THROUGH_THE_TIP = [[10.0, 0.0, 180.0], [10.0, 0.0, 140.0]]
HIGH_THROUGH_THE_WALL = [[20.0, 0.0, 155.0], [10.0, 0.0, 155.0]]


def interstitial_length(needle: list[list[float]]) -> float:
    """Return the reference sheet's interstitial length for one needle in a 30 mm by 160 mm cylinder.

    A helper, not a test. The cylinder is built from the live settings, so each test sets the
    tip first. The needle's first point is its tip, as in a plan.
    """
    from classes.mesh.cylinder import BrachyCylinder
    from classes.pdf.template_reference import get_all_interstitial_lengths

    return get_all_interstitial_lengths(cylinder=BrachyCylinder(diameter=30.0), needles=[needle])[0]


def test_a_needle_leaving_a_dome_10_mm_off_axis_is_measured_from_the_dome(
    default_settings: dict[str, float],
) -> None:
    """Check a needle tip at z 180, 10 mm off the axis, is 23.82 mm beyond the dome.

    The dome is a 15 mm half-sphere on 145 mm of wall, so 10 mm off the axis its surface is at
    145 + sqrt(15^2 - 10^2) = 156.18 mm. Fails if the dome measurement changes, which would
    print every dome cylinder's interstitial lengths wrong.
    """
    assert interstitial_length(THROUGH_THE_TIP) == pytest.approx(23.82, abs=0.1)


def test_a_needle_leaving_a_flat_tip_is_measured_from_the_flat_top(
    default_settings: dict[str, float],
) -> None:
    """Check the same needle in a flat-tipped cylinder is 20 mm beyond the top at z 160.

    Fails if the length is still measured against a dome, which prints 23.82 mm instead. The
    clinician sets the needle's protrusion from this number, so it would be off by 3.8 mm in
    the patient.
    """
    default_settings["CONFIG_CYLINDER_FLAT_TIP"] = 1
    assert interstitial_length(THROUGH_THE_TIP) == pytest.approx(20.0, abs=0.1)


def test_a_flat_tip_keeps_its_wall_up_to_the_top(default_settings: dict[str, float]) -> None:
    """Check a sideways needle at z 155 leaves a flat-tipped cylinder's wall at x 15, 5 mm from its tip.

    A dome starts curving in at z 145, so there its surface is at x 11.18 and the length would
    be 8.82 mm. Fails if the flat-tip surface stops the wall where a dome would begin, which
    would misprint every needle leaving the top 15 mm of the wall.
    """
    default_settings["CONFIG_CYLINDER_FLAT_TIP"] = 1
    assert interstitial_length(HIGH_THROUGH_THE_WALL) == pytest.approx(5.0, abs=0.1)


def test_the_default_notch_is_drawn_standing_out_of_the_circle_at_anterior() -> None:
    """Check the default notch's corners on the sheet, for a 15 mm radius.

    The sheet draws Anterior at the top, so the 2 mm wide notch spans x -1 to 1 and stands
    1.8 mm out of the circle, y 15 to 16.8. Fails if the drawing is not where or how big the
    printed notch is, which would make the QA orientation check against the sheet wrong.
    """
    from classes.mesh.notch import NotchSettings
    from classes.pdf.template_reference import notch_outline

    corners = notch_outline(NotchSettings(), 15.0)
    expected = [(-1.0, 15.0), (1.0, 15.0), (1.0, 16.8), (-1.0, 16.8)]
    assert corners == [pytest.approx(corner) for corner in expected]


def test_a_notch_a_quarter_turn_clockwise_is_drawn_on_the_right() -> None:
    """Check a notch at 90 degrees is drawn on the right of the circle, x 15 to 16.8.

    Fails if the drawing turns the wrong way or not at all, so the sheet would show the mark on
    a different side from the printed cylinder.
    """
    from classes.mesh.notch import NotchSettings
    from classes.pdf.template_reference import notch_outline

    corners = notch_outline(NotchSettings(angle=90.0), 15.0)
    expected = [(15.0, 1.0), (15.0, -1.0), (16.8, -1.0), (16.8, 1.0)]
    assert corners == [pytest.approx(corner) for corner in expected]


def test_a_notch_turned_off_is_not_drawn() -> None:
    """Check a disabled notch has no outline on the sheet.

    Fails if a rectangle is still drawn, showing an orientation mark the cylinder does not have.
    """
    from classes.mesh.notch import NotchSettings
    from classes.pdf.template_reference import notch_outline

    assert notch_outline(NotchSettings(enabled=False), 15.0) == []


def test_the_anterior_label_clears_the_notch() -> None:
    """Check Anterior is placed 18.3 from the centre, 1.5 beyond a 1.8 mm notch on a 15 mm circle.

    Fails if the label is placed where the notch is drawn, as it was at 16.5, which printed the
    rectangle over the word Anterior.
    """
    from classes.mesh.notch import NotchSettings
    from classes.pdf.template_reference import label_distance

    assert label_distance(15.0, NotchSettings()) == pytest.approx(18.3)


def test_the_cylinder_table_lists_the_default_cylinder(default_settings: dict[str, float]) -> None:
    """Check the reference sheet's cylinder table for the default 30 mm by 160 mm cylinder.

    Fails if a value is missing or wrong, which would let the QA team pass a printed cylinder
    that does not match the design. The text has no colon, per the UI copy rule.
    """
    from classes.mesh.cylinder import BrachyCylinder
    from classes.pdf.template_reference import cylinder_rows

    cylinder = BrachyCylinder(diameter=30.0)
    cylinder.enableBase(False)
    assert cylinder_rows(cylinder) == [
        ["Diameter", "30.0 mm"],
        ["Length", "160.0 mm"],
        ["Tip", "Dome"],
        ["Notch", "At 0.0°, 2.0 mm wide, 1.8 mm deep, 10.0 mm high"],
        ["Collar", "None"],
    ]


def test_the_cylinder_table_shows_a_flat_tip_no_notch_and_a_collar(
    default_settings: dict[str, float],
) -> None:
    """Check the table for a flat tip, the notch off, and a 3 mm by 10 mm collar.

    Fails if any of the three is reported as the default. A flat tip cannot be seen in the
    sheet's cross-section, so this row is the only place the sheet shows it.
    """
    from classes.mesh.cylinder import BrachyCylinder
    from classes.pdf.template_reference import cylinder_rows

    default_settings["CONFIG_CYLINDER_FLAT_TIP"] = 1
    default_settings["CONFIG_NOTCH_ENABLED"] = 0
    default_settings["CONFIG_BASE_THICKNESS"] = 3.0
    default_settings["CONFIG_BASE_HEIGHT"] = 10.0
    cylinder = BrachyCylinder(diameter=30.0)
    cylinder.enableBase(True)
    assert cylinder_rows(cylinder)[2:] == [
        ["Tip", "Flat"],
        ["Notch", "Off"],
        ["Collar", "3.0 mm thick, 10.0 mm high"],
    ]
