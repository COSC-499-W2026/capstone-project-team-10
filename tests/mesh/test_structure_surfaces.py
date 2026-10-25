"""Surface reconstruction retains anatomy boundaries rather than joining ROI loops."""
import numpy as np
import pytest
from classes.dicom.structures import Contour


def square(z: float, low: float = -4., high: float = 4., kind: str = 'CLOSED_PLANAR') -> Contour:
    """Build a literal square slice for tests, not an inferred production surface.

    Its known bounds and interior expose misplaced vertices and lost holes.
    """
    return Contour(kind, ((low, low, z), (high, low, z), (high, high, z), (low, high, z)))


def test_surface_is_closed_and_preserves_patient_bounds():
    """Reconstruct a square stack in patient coordinates as a closed triangle mesh.

    Wrong axis order, missing caps or duplicated triangle vertices fails; a misplaced
    surface would give a misleading relationship to the probe.
    """
    from classes.mesh.structure_surfaces import reconstruct_surface
    mesh = reconstruct_surface(tuple(square(z) for z in (10., 12., 14.)), spacing=0.5)
    vertices = mesh.vertices
    assert vertices.min(axis=0) == pytest.approx((-4.25, -4.25, 10.), abs=0.3)
    assert vertices.max(axis=0) == pytest.approx((4.25, 4.25, 14.), abs=0.3)
    edges = np.sort(np.concatenate((mesh.triangles[:, :2], mesh.triangles[:, 1:], mesh.triangles[:, (2, 0)])), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    assert np.all(counts == 2)


def test_xor_hole_remains_empty_and_separate_regions_do_not_bridge():
    """Preserve a hole and a separated island in sampled anatomy.

    A union in place of XOR or connecting all outlines fills the centre or gap and
    fails these literal mask checks, inventing tissue where none was contoured.
    """
    from classes.mesh.structure_surfaces import sample_contours
    contours = tuple(c for z in (0., 2., 4.) for c in (
        square(z, -4., 4., 'CLOSEDPLANAR_XOR'), square(z, -2., 2., 'CLOSEDPLANAR_XOR'),
        square(z, 8., 10., 'CLOSEDPLANAR_XOR')))
    volume = sample_contours(contours, spacing=0.5)
    for point, expected in [((0., 0., 2.), False), ((3., 3., 2.), True), ((6., 6., 2.), False), ((9., 9., 2.), True)]:
        index = np.rint((np.array(point) - volume.origin) / volume.spacing).astype(int)
        assert bool(volume.values[tuple(index)] > 0) == expected


@pytest.mark.parametrize('contours', [
    (square(0.),),
    (square(0.), square(1.), square(10.)),
    (Contour('OPEN_PLANAR', ((0., 0., 0.), (1., 0., 0.))),),
])
def test_unsupported_stacks_are_reported_instead_of_inventing_surfaces(contours):
    """Reject a single slice, a large missing-slice gap and open contours.

    Accepting these inputs fails; unknown volume extent or missing anatomy must
    remain an outline preview instead of becoming an apparently complete organ.
    """
    from classes.mesh.structure_surfaces import reconstruct_surface
    with pytest.raises(ValueError):
        reconstruct_surface(contours)


def test_dense_slice_stacks_respect_the_memory_budget():
    """Bound intermediate slice fields as well as the final voxel grid.

    A dense stack with a shallow Z extent fails if all intermediate fields are
    allocated despite exceeding the budget; otherwise importing can freeze the UI.
    """
    from classes.mesh.structure_surfaces import sample_contours
    with pytest.raises(ValueError, match='size limit'):
        sample_contours(tuple(square(index * 0.02, 0., 1000.) for index in range(30)))


def test_surface_triangles_face_outward():
    """Orient a closed square stack away from the tissue interior.

    Negative signed volume fails when marching cubes reverses the winding;
    inward normals incorrectly light the organ preview from inside the tissue.
    """
    from classes.mesh.structure_surfaces import reconstruct_surface
    mesh = reconstruct_surface(tuple(square(z) for z in (10., 12., 14.)), spacing=0.5)
    a, b, c = np.moveaxis(mesh.vertices[mesh.triangles], 1, 0)
    signed_volume = np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6
    assert signed_volume > 0
