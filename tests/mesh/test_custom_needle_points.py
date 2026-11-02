"""Exercise src/classes/mesh/helper.py: the points of a custom needle and the rules its start and lengths must meet."""
from __future__ import annotations

import pytest

from classes.mesh.helper import CustomNeedleError, CustomNeedleSpec, custom_needle_points


def build(spec: CustomNeedleSpec) -> list[list[float]]:
    """Build a spec's points in a 30 mm wide, 100 mm long cylinder with a 3 mm needle. A helper, not a test."""
    return custom_needle_points(spec, 30.0, 100.0, 3.0)


def needle(x: float = 0.0, y: float = 0.0, length1: float = 40.0, length2: float = 25.0) -> CustomNeedleSpec:
    """Make a spec with the given numbers, defaulting to the centre and lengths of 40 and 25. A helper, not a test."""
    return CustomNeedleSpec(label="a", x=x, y=y, length1=length1, length2=length2)


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
