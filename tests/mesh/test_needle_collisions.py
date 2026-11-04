"""Known closed volumes and needle paths exercise possible organ intersections."""
import numpy as np
import pytest


def cube():
    """Return a closed, outward cube with literal bounds ±1 for geometry tests.

    Incorrect face winding or coordinates breaks inside and grazing assertions;
    these fixtures prevent missed organ warnings without sampling DICOM data.
    """
    from classes.mesh.structure_surfaces import AnatomySurface
    vertices = np.array([[-1,-1,-1], [1,-1,-1], [1,1,-1], [-1,1,-1],
                         [-1,-1,1], [1,-1,1], [1,1,1], [-1,1,1]], dtype=float)
    faces = np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                      [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]], dtype=np.int32)
    return AnatomySurface(vertices, faces)


@pytest.mark.parametrize('points,radius,expected', [
    (((-5.,0.,0.), (5.,0.,0.)), 0.1, True),
    (((0.,0.,0.), (0.5,0.,0.)), 0.1, True),
    (((-5.,3.,0.), (5.,3.,0.)), 0.1, False),
    (((-5.,1.4,0.), (5.,1.4,0.)), 0.5, True),
    (((-5.,1.4,0.), (5.,1.4,0.)), 0.1, False),
    (((2.,2.,2.), (3.,3.,3.)), 0.1, False),
    (((0.,0.,0.), (0.,0.,0.)), 0.1, True),
])
def test_needle_capsule_intersects_organ(points, radius, expected):
    """Detect crossings, containment and radius contact but reject clear paths.

    A wrong inside test, ignored shaft radius or skipped long segment fails the
    literal expectations and could hide a needle passing through an organ.
    """
    from classes.mesh.needle_collisions import CollisionSurface, NeedlePath
    surface = CollisionSurface(cube())
    assert surface.intersects(NeedlePath('needle', points, radius)) == expected


def test_disconnected_organs_do_not_fill_the_gap():
    """Keep the empty space between disconnected closed components clear.

    Replacing tissue with its bounding box flags the middle needle and fails;
    an organ envelope must not invent tissue between separate contours.
    """
    from classes.mesh.needle_collisions import CollisionSurface, NeedlePath
    from classes.mesh.structure_surfaces import AnatomySurface
    part = cube()
    surface = AnatomySurface(np.concatenate((part.vertices + (0,4,0), part.vertices - (0,4,0))),
                             np.concatenate((part.triangles, part.triangles + 8)))
    assert not CollisionSurface(surface).intersects(NeedlePath('gap', ((-5.,0.,0.),(5.,0.,0.)), 0.2))


def test_invalid_path_is_not_reported_as_clear():
    """Reject nonfinite coordinates rather than interpreting them as no collision.

    Accepting a NaN fails the exception assertion and could present missing
    geometry as a checked organ.
    """
    from classes.mesh.needle_collisions import NeedlePath
    with pytest.raises(ValueError):
        NeedlePath('invalid', ((float('nan'),0.,0.),(1.,0.,0.)), 0.2)


def test_closed_cavity_remains_clear():
    """Respect inward-facing cavity walls instead of filling a hollow organ.

    Taking absolute solid angles per face flags the central path and fails;
    XOR contour holes must not become false tissue warnings.
    """
    from classes.mesh.needle_collisions import CollisionSurface, NeedlePath
    from classes.mesh.structure_surfaces import AnatomySurface
    part = cube()
    hollow = AnatomySurface(np.concatenate((part.vertices * 4., part.vertices * 2.)),
                            np.concatenate((part.triangles, (part.triangles + 8)[:, ::-1])))
    surface = CollisionSurface(hollow)
    assert not surface.intersects(NeedlePath('inside cavity', ((0.,0.,-1.),(0.,0.,1.)), 0.2))
    assert surface.intersects(NeedlePath('through wall', ((0.,0.,0.),(0.,0.,5.)), 0.2))
