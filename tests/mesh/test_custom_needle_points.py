"""Exercise src/classes/mesh/helper.py: the points of a custom needle and the rules its start and lengths must meet."""
from __future__ import annotations

import pytest

from classes.mesh.helper import CustomNeedleError, CustomNeedleSpec, custom_needle_points


def build(spec: CustomNeedleSpec) -> list[list[float]]:
    """Build a spec's points in a 30 mm wide, 100 mm long cylinder with a 3 mm needle. A helper, not a test."""
    return custom_needle_points(spec, 30.0, 100.0, 3.0)


def needle(x: float = 0.0, y: float = 0.0, length1: float = 40.0, length2: float = 25.0,
           radius: float = 0.0, theta: float = 0.0, phi: float = 0.0) -> CustomNeedleSpec:
    """Make a spec with the given numbers, defaulting to a straight needle at the centre with lengths of 40 and 25. A helper, not a test."""
    return CustomNeedleSpec(label="a", x=x, y=y, length1=length1, length2=length2, radius=radius, theta=theta, phi=phi)


def test_the_points_run_from_the_tissue_end_down_to_the_base() -> None:
    """Check a start of (3, -2) with lengths 40 and 25 gives the tip at z 65 first and the base at z 0 last.

    Fails if the list is base first, or the tip is not Length 1 plus Length 2. The channel builder
    adds the dead space at the first point, so a reversed list leaves the needle short of the
    tissue on a patient's applicator.
    """
    assert build(needle(x=3.0, y=-2.0)) == [[3.0, -2.0, 65.0], [3.0, -2.0, 0.0]]


@pytest.mark.parametrize("bad", [needle(length1=0.0), needle(length1=-1.0), needle(length2=0.0), needle(length2=-5.0),
                                 needle(length1=100.5), needle(x=13.6), needle(x=float("nan")), needle(length2=float("inf"))])
def test_numbers_that_break_a_rule_are_refused_in_plain_text(bad: CustomNeedleSpec) -> None:
    """Check a length of zero or less, a Length 1 over 100, a start 13.6 mm out, NaN and infinity all raise CustomNeedleError.

    Fails if one is built, or if its text has a colon or an em dash, which AGENTS.md bans in copy
    a clinician reads. A zero length gives two equal points and a NaN crashed OpenCASCADE for a
    channel's diameter (exit 139), so either would take the app down at the cut.
    """
    with pytest.raises(CustomNeedleError) as refusal:
        build(bad)
    assert ":" not in str(refusal.value) and "—" not in str(refusal.value)


def test_the_limits_are_kept_exactly_on_the_edge() -> None:
    """Check a start 13.5 mm from the axis and a Length 1 of 100 mm are both kept.

    Fails if the start limit is the cylinder's 15 mm radius, which lets the needle's wall break
    the side and leaves a slot instead of a channel, or if either limit is off by a little.
    """
    assert build(needle(x=13.5))[1] == [13.5, 0.0, 0.0]
    assert build(needle(length1=100.0))[0] == [0.0, 0.0, 125.0]


@pytest.mark.parametrize("spec, tip", [
    (needle(radius=5.0, theta=60.0), (24.150635, 0.0, 56.830127)),
    (needle(x=3.0, y=-2.0, radius=5.0, theta=60.0, phi=90.0), (3.0, 22.150635, 56.830127)),
    (needle(radius=10.0, theta=30.0), (13.839746, 0.0, 66.650635)),
])
def test_a_bend_turns_the_needle_by_theta_towards_phi_after_a_radius_arc(spec: CustomNeedleSpec, tip: tuple[float, float, float]) -> None:
    """Check the tip of a bent needle for a 60 degree turn towards +X, one towards +Y from (3, -2), and a 30 degree turn.

    Fails if the arc ends at the wrong place, Phi is not measured from +X towards +Y, Theta is
    measured from the base instead of the cylinder's axis, or Length 2 does not follow the
    bent direction. The tip is where the clinician expects the needle to reach tissue, so a
    wrong direction puts the source in the wrong place on a patient.
    """
    assert build(spec)[0] == pytest.approx(list(tip), abs=1e-5)


def test_a_bend_is_sampled_along_the_arc_from_the_joint_to_the_arc_end() -> None:
    """Check a 60 degree bend of radius 5 gives nine points, the base, the joint at z 40, the arc end and the tip.

    Fails if the arc is one straight chord, which cuts the corner of the bend, or the joint
    or arc end is missing. rounded_channel joins points with straight pipes, so too few points
    would print a kink instead of a curve and the source could not pass.
    """
    points = build(needle(radius=5.0, theta=60.0))

    assert len(points) == 9
    assert points[-1] == [0.0, 0.0, 0.0] and points[-2] == pytest.approx([0.0, 0.0, 40.0])
    assert points[1] == pytest.approx([2.5, 0.0, 44.330127])


def test_theta_zero_stays_straight_whatever_the_radius_and_phi() -> None:
    """Check Theta 0 with a radius and a Phi still gives the two straight points.

    Fails if a turn of nothing adds arc points. Opening the form and typing only the lengths must
    still give the straight needle that a Radius or Phi left at a value cannot change.
    """
    assert build(needle(radius=7.0, phi=45.0)) == [[0.0, 0.0, 65.0], [0.0, 0.0, 0.0]]


@pytest.mark.parametrize("bad", [needle(theta=-1.0), needle(radius=5.0, theta=90.0), needle(radius=5.0, theta=float("nan")),
                                 needle(radius=0.0, theta=30.0), needle(radius=-2.0, theta=30.0),
                                 needle(radius=5.0, theta=30.0, phi=float("inf"))])
def test_a_bend_with_a_theta_or_radius_it_cannot_make_is_refused_in_plain_text(bad: CustomNeedleSpec) -> None:
    """Check a Theta below 0 or at 90, NaN, a bend with no radius and an infinite Phi all raise CustomNeedleError.

    Fails if one is built, or its text has a colon or an em dash. Exactly 90 leaves the last pipe
    flat, which makes rounded_channel's sphere fuse warn and open its error box, and a NaN
    reaches OpenCASCADE, which crashed the app before (exit 139).
    """
    with pytest.raises(CustomNeedleError) as refusal:
        build(bad)
    assert ":" not in str(refusal.value) and "—" not in str(refusal.value)
