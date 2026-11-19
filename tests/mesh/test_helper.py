"""Exercise rotate_points in src/classes/mesh/helper.py: the DICOM to cylinder Rodrigues transform."""
from __future__ import annotations

import numpy as np
import pytest

from classes.mesh.helper import rotate_points


def test_identical_axes_leave_every_point_unchanged() -> None:
    """Check that aligning a vector to itself returns the same (n,3) cloud.

    Fails if any coordinate moves when v1 equals v2. Import skips a rotation in that case, so a
    changed cloud would shift every needle even when the plan axis already points at +Z.
    """
    points = np.array([[1.0, 2.0, 3.0], [-4.0, 0.5, 10.0], [0.0, 0.0, 0.0]])
    axis = np.array([0.0, 0.0, 7.0])

    result = rotate_points(points, axis, axis)

    assert result == pytest.approx(points)


def test_a_point_on_v1_lands_on_v2_after_a_right_angle_realign() -> None:
    """Check that a tip on +X lands on +Z, and a +Y neighbour stays put, for +X to +Z.

    Fails if the tip is not [0, 0, 1] or the neighbour leaves [0, 1, 0]. fileio rotates every
    channel from the cylinder direction onto +Z, so a wrong Rodrigues step puts every needle
    off the printed axis. The cloud has two rows on purpose: a single-row (1, 3) array still
    takes the `np.size == 3` branch and raises (§7.29).
    """
    points = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    result = rotate_points(points, np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))

    assert result == pytest.approx(np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]))


def test_a_cloud_keeps_pairwise_distances_when_the_axis_turns_ninety_degrees() -> None:
    """Check that three points keep every pairwise distance after a +Y to +Z realign.

    Fails if any distance changes. Rotation must be rigid, or channel lengths and spacing change
    and the cut holes no longer match the plan.
    """
    points = np.array([[2.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 4.0]])
    before = (
        np.linalg.norm(points[0] - points[1]),
        np.linalg.norm(points[0] - points[2]),
        np.linalg.norm(points[1] - points[2]),
    )

    result = rotate_points(points, np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0]))
    after = (
        np.linalg.norm(result[0] - result[1]),
        np.linalg.norm(result[0] - result[2]),
        np.linalg.norm(result[1] - result[2]),
    )

    assert result.shape == (3, 3)
    assert after == pytest.approx(before)


def test_a_single_point_vector_returns_three_coordinates_not_a_one_row_matrix() -> None:
    """Check that an input with np.size 3 returns a length-3 vector after a +X to +Z realign.

    Fails if the result is shape (1, 3) or the values are not [0, 0, 1]. The import path sometimes
    hands a lone base point through this branch, and a nested row breaks the later base subtract.
    """
    point = np.array([1.0, 0.0, 0.0])

    result = rotate_points(point, np.array([2.0, 0.0, 0.0]), np.array([0.0, 0.0, 5.0]))

    assert np.shape(result) == (3,)
    assert result == pytest.approx(np.array([0.0, 0.0, 1.0]))
