"""Exercise spec_from_points in src/classes/mesh/helper.py: the Edit form's numbers for an imported needle."""
from __future__ import annotations

import pytest

from classes.mesh.helper import MAX_THETA_DEGREES, CustomNeedleError, CustomNeedleSpec, spec_from_points

TILT = 17.67767  # 25 mm of path at 45 degrees goes this far sideways and this far up


def numbers(spec: CustomNeedleSpec) -> tuple[float, ...]:
    """Return a spec's x, y, length1, length2, radius, theta and phi as a tuple. A helper, not a test."""
    return (spec.x, spec.y, spec.length1, spec.length2, spec.radius, spec.theta, spec.phi)


def test_a_straight_vertical_needle_keeps_its_start_and_its_total_length() -> None:
    """Check a vertical needle from (3, -2) up to z 65 gives that start, a total length of 65 and no bend.

    Fails if the start is not the point on the base, if the two lengths do not add up to the
    needle's height, or if a bend appears. The form must show a straight needle as straight, or
    pressing OK would bend a needle the plan aimed straight up. Length 2 is the smallest the form
    allows, 0.001 mm, because the form refuses a Length 2 of 0.
    """
    spec = spec_from_points("Applicator2", [[3.0, -2.0, 65.0], [3.0, -2.0, 0.0]])

    assert spec.label == "Applicator2"
    assert numbers(spec) == pytest.approx((3.0, -2.0, 64.999, 0.001, 0.0, 0.0, 0.0))


def test_a_needle_that_drops_straight_to_the_base_after_a_tilt_gives_the_drop_as_length_1() -> None:
    """Check a needle tilted 45 degrees towards +X above a vertical run of 40 gives Length 1 of 40, Length 2 of 25 and Theta 45.

    Fails if Length 1 is not the vertical run, which is how the export threads and drops an
    imported channel to the base, or if Theta or Phi is wrong. The rebuilt needle would then
    enter the tissue somewhere other than where the plan put it.
    """
    spec = spec_from_points("a", [[3.0 + TILT, -2.0, 40.0 + TILT], [3.0, -2.0, 40.0]])

    assert numbers(spec) == pytest.approx((3.0, -2.0, 40.0, 25.0, 1.0, 45.0, 0.0), abs=1e-4)


@pytest.mark.parametrize(("tip_x", "tip_y", "phi"), [(3.0, -2.0 + TILT, 90.0), (3.0 - TILT, -2.0, 180.0), (3.0, -2.0 - TILT, 270.0)])
def test_phi_is_the_direction_of_the_tilt_from_x_towards_y_in_every_quadrant(tip_x: float, tip_y: float, phi: float) -> None:
    """Check a tilt towards +Y, -X and -Y gives a Phi of 90, 180 and 270, never a negative angle.

    Fails if atan2's negative angle is passed on, because the form's Phi runs from 0 to 360 and
    its box would stop at 0, so every needle tilted towards -Y, most of the Ex1 plan, could not
    be shown in the form.
    """
    spec = spec_from_points("a", [[tip_x, tip_y, 40.0 + TILT], [3.0, -2.0, 40.0]])

    assert spec.phi == pytest.approx(phi, abs=1e-4) and spec.theta == pytest.approx(45.0, abs=1e-4)


def test_a_tilted_needle_that_ends_on_the_base_starts_there_with_the_smallest_length_1() -> None:
    """Check a straight needle from (20, 0, 40) down to (0, 0, 0) starts at (0, 0) with Length 1 of 0.001 and Theta 26.565.

    Fails if there is a Length 1 of 0, which the form refuses, so the clinician could not press
    OK, or if Length 2 is not the whole path length of 44.721, which would shorten the needle.
    """
    spec = spec_from_points("a", [[20.0, 0.0, 40.0], [0.0, 0.0, 0.0]])

    assert numbers(spec) == pytest.approx((0.0, 0.0, 0.001, 44.7214, 1.0, 26.5651, 0.0), abs=1e-4)


def test_a_needle_that_crosses_the_base_starts_where_it_meets_it() -> None:
    """Check a straight needle from (10, 0, 20) down to (0, 0, -20) starts at x 5 on the base with Theta 14.036.

    Fails if the start is the last point at x 0 below the base, because the form's start is on
    the base and the needle would be rebuilt 5 mm from where it enters the cylinder.
    """
    spec = spec_from_points("a", [[10.0, 0.0, 20.0], [0.0, 0.0, -20.0]])

    assert numbers(spec) == pytest.approx((5.0, 0.0, 0.001, 20.6155, 1.0, 14.0362, 0.0), abs=1e-4)


def test_a_curved_path_keeps_its_tip_by_using_the_straight_distance_to_it() -> None:
    """Check a three point path from (0, 0, 30) to a tip at (6, 0, 36) gives Length 2 of 8.485 and Theta 45.

    Fails if the estimate uses the path length of the longer curve, which would carry the tip
    past where the plan put it, or the angle of one segment. The dwell positions are measured
    from the tip, so a moved tip changes where the source stops.
    """
    spec = spec_from_points("a", [[6.0, 0.0, 36.0], [4.0, 0.0, 33.0], [0.0, 0.0, 30.0]])

    assert numbers(spec) == pytest.approx((0.0, 0.0, 30.0, 8.4853, 1.0, 45.0, 0.0), abs=1e-4)


def test_a_needle_tilted_past_the_form_limit_is_given_the_largest_theta_the_form_allows() -> None:
    """Check a nearly flat needle gives Theta of exactly the form's maximum.

    Fails if Theta is above the limit, because the form's box would clamp it silently while
    the model refuses it, or the needle could not be edited at all.
    """
    spec = spec_from_points("a", [[100.0, 0.0, 1.0], [0.0, 0.0, 0.5]])

    assert spec.theta == MAX_THETA_DEGREES


@pytest.mark.parametrize("bad", [[], [[1.0, 2.0, 3.0]], [[0.0, 0.0, 5.0], [float("nan"), 0.0, 0.0]], [[0.0, 0.0, 5.0], [0.0, 0.0, float("inf")]]])
def test_a_path_that_cannot_give_numbers_is_refused_in_plain_text(bad: list[list[float]]) -> None:
    """Check no points, one point, NaN and infinity each raise CustomNeedleError with no colon or em dash.

    Fails if one is accepted, because NaN reaching the geometry crashes OpenCASCADE (exit 139),
    or if the text has a colon or em dash, which AGENTS.md bans in copy a clinician reads.
    """
    with pytest.raises(CustomNeedleError) as refusal:
        spec_from_points("a", bad)

    assert ":" not in str(refusal.value) and "—" not in str(refusal.value)
