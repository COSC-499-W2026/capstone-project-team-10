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
