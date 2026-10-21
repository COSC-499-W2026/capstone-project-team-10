"""Patient-to-probe alignment for anatomy contour previews."""
import pytest
from classes.dicom.structures import Contour
import numpy as np
from classes.mesh import structure_contours


def test_contour_transform_keeps_tip_alignment_and_closed_boundary():
    """Map an X-directed probe to Z with its tip at the configured length.

    Wrong rotation or translation fails the literal coordinates and would place
    anatomy beside the wrong needle. Source contours must remain unchanged.
    """
    contour = Contour('CLOSED_PLANAR', ((10., 20., 30.), (10., 22., 30.), (10., 22., 32.)))
    alignment = structure_contours.ContourAlignment((10., 20., 30.), (10., 0., 0.), 20., 'frame')
    result = structure_contours.transform_contour(contour, alignment)
    np.testing.assert_allclose(result.points, ((0., 0., 10.), (0., 2., 10.), (-2., 2., 10.)), atol=1e-10)
    assert contour.points[0] == (10., 20., 30.)


def test_alignment_rejects_missing_frame_and_degenerate_axis():
    """Reject registration without an identified frame or usable probe axis.

    Accepting either case fails and could display anatomy in an unrelated frame.
    """
    for direction, frame in [((0., 0., 0.), 'frame'), ((0., 0., 1.), '')]:
        with pytest.raises(ValueError):
            structure_contours.ContourAlignment((0., 0., 0.), direction, 160., frame)


def test_closed_outline_has_all_edges_and_no_filled_faces():
    """Build a closed triangular outline, removing an explicit duplicate endpoint.

    Missing the final edge or creating a filled face fails; this preview must show
    the supplied contour boundary without claiming a reconstructed organ surface.
    """
    from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCC.Core.TopExp import TopExp_Explorer
    contour = Contour('CLOSED_PLANAR', ((0., 0., 0.), (2., 0., 0.), (0., 2., 0.), (0., 0., 0.)))
    shape = structure_contours.contour_outline((contour,))
    edges = TopExp_Explorer(shape, TopAbs_EDGE)
    count = 0
    while edges.More():
        count += 1
        edges.Next()
    assert count == 3
    assert not TopExp_Explorer(shape, TopAbs_FACE).More()


def test_point_array_alignment_preserves_input_and_patient_registration():
    """Align mesh vertices directly without modifying cached patient coordinates.

    Incorrect rotation, tip translation or an in-place edit fails these literal
    coordinates and could move anatomy relative to the probe on later redraws.
    """
    points = np.array(((10., 20., 30.), (10., 22., 32.)))
    alignment = structure_contours.ContourAlignment((10., 20., 30.), (10., 0., 0.), 20., 'frame')
    aligned = structure_contours.transform_points(points, alignment)
    np.testing.assert_allclose(aligned, ((0., 0., 10.), (-2., 2., 10.)), atol=1e-10)
    np.testing.assert_array_equal(points, ((10., 20., 30.), (10., 22., 32.)))
