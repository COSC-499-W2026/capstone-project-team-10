import math
from dataclasses import dataclass

import numpy as np

from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.GeomAbs import GeomAbs_Plane
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods, TopoDS_Face, TopoDS_Shape
from OCC.Core.gp import gp_Dir, gp_Ax2, gp_Pnt, gp_Pln, gp_Vec, gp_Circ
from OCC.Extend.ShapeFactory import translate_shp, rotate_shape


def face_is_plane(face: TopoDS_Face) -> bool:
    """
    Returns True if the TopoDS_Face is a plane, False otherwise
    """
    surf = BRepAdaptor_Surface(face, True)
    surf_type = surf.GetType()
    return surf_type == GeomAbs_Plane


def geom_plane_from_face(face: TopoDS_Face) -> gp_Pln:
    """
    Returns the geometric plane entity from a planar surface
    """
    return BRepAdaptor_Surface(face, True).Plane()


def get_faces(shape: TopoDS_Shape) -> list[TopoDS_Face]:
    '''
    returns a list of planar faces for the shape from highest to lowest
    '''

    def sortByZ(elem):
        return elem[1]

    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces = []
    while explorer.More():
        face = topods.Face(explorer.Current())
        if face_is_plane(face):
            a_plane = geom_plane_from_face(face)
            # face with it's z height
            faces.append([face, a_plane.Location().Z()])
        explorer.Next()
    faces.sort(key=sortByZ)
    return faces


def get_faces_axis(shape: TopoDS_Shape) -> list:
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces = []
    while explorer.More():
        face = topods.Face(explorer.Current())
        if face_is_plane(face):
            a_plane = geom_plane_from_face(face)
            faces.append([face, a_plane.Axis(), a_plane.Location()])
        explorer.Next()
    return faces


def lowest_face_by_normal(shape: TopoDS_Shape) -> TopoDS_Face:
    faces = get_faces_axis(shape)

    # check for the lowest face
    def sortByZ(elem):
        return elem[2].Z()

    faces.sort(key=sortByZ)
    return faces[0]
'''
def get_highest_face(shape: TopoDS_Shape) -> TopoDS_Face:
    faces = get_faces(shape)
    return faces[-1][0]


def get_lowest_face(shape: TopoDS_Shape) -> TopoDS_Face:
    faces = get_faces(shape)
    return faces[0][0]
'''
def get_vector(p1: gp_Pnt, p2: gp_Pnt, length: float = 1.0) -> gp_Vec:
    vector = gp_Vec(
        p2.X() - p1.X(),
        p2.Y() - p1.Y(),
        p2.Z() - p1.Z())
    try:
        vn = vector.Normalized()
    except:
        print("Error: vector is zero")
    return vector.Normalized() * length


def get_magnitude(p1: gp_Pnt, p2: gp_Pnt) -> float:
    vector = np.array([p2.X(), p2.Y(), p2.Z()]) \
        - np.array([p1.X(), p1.Y(), p1.Z()])
    return np.linalg.norm(vector) # (defaults to 2-norm)


def get_direction(p1: gp_Pnt, p2: gp_Pnt) -> gp_Dir:
    vector = get_vector(p1, p2) #p2-p1*length where p2 and p1 are vectors and length is 1 by default
    return gp_Dir(vector.X(), vector.Y(), vector.Z()) #gives normalized vector


def get_vector_from_angle(v1: gp_Vec = gp_Vec(1, 0, 0), angle: float = 0.0, length: float = 1.0) -> gp_Vec:
    x = math.cos(angle)
    y = math.sin(angle)
    result = gp_Vec(v1.X() + x, v1.Y(), v1.Z()).Normalized()
    return result * length


def extend_bottom_face(shape: TopoDS_Shape) -> TopoDS_Shape:
    face = lowest_face_by_normal(shape)
    z = face[2].Z()
    # ensures no erroronious z value
    if(z!=0.0001):
        direction = gp_Vec(0, 0, -z - 0.0001)
    else:
        direction = gp_Vec(0, 0, -z - 0.0002)

    extended_geometry = BRepPrimAPI_MakePrism(face[0], direction).Shape()
    return BRepAlgoAPI_Fuse(shape, extended_geometry).Shape()


def translate_shape(shape: TopoDS_Shape, vector: gp_Vec) -> TopoDS_Shape:
    return translate_shp(shape, vector).Shape()


def rotate_points(points, v_1, v_2):
    # V1 is the current vector which the coordinate system is aligned to
    # V2 is the vector we want the system aligned to
    # Points is an (n,3) array of n points (x,y,z)
    v_1 = np.asarray(v_1)
    v_2 = np.asarray(v_2)

    # Normalize V1 and V2 in case they aren't already
    len_1 = (v_1[0] ** 2 + v_1[1] ** 2 + v_1[2] ** 2) ** 0.5
    len_2 = (v_2[0] ** 2 + v_2[1] ** 2 + v_2[2] ** 2) ** 0.5
    v_1 = v_1 / len_1
    v_2 = v_2 / len_2

    if np.array_equal(v_1, v_2):  # points do not need to be rotated
        return points

    # Calculate the vector cross product
    cross_v1v2 = np.cross(v_1, v_2)
    cross_norm = (cross_v1v2[0] ** 2 + cross_v1v2[1]
                  ** 2 + cross_v1v2[2] ** 2) ** 0.5
    cross_normalized = cross_v1v2 / cross_norm

    # Dot product
    dot_v1v2 = np.dot(v_1, v_2)
    v1_norm = (v_1[0] ** 2 + v_1[1] ** 2 + v_1[2] ** 2) ** 0.5
    v2_norm = (v_2[0] ** 2 + v_2[1] ** 2 + v_2[2] ** 2) ** 0.5

    # Angle between the vectors
    theta = np.arccos(dot_v1v2 / (v1_norm * v2_norm))

    # Using Rodrigues' rotation formula (wikipedia):
    e = cross_normalized

    pts_rotated = np.empty((len(points), 3))
    if np.size(points) == 3:
        p = points
        p_rotated = np.cos(theta) * p + np.sin(theta) * \
            (np.cross(e, p)) + (1 - np.cos(theta)) * np.dot(e, p) * e
        pts_rotated = p_rotated
    else:
        for i, p in enumerate(points):
            p_rotated = np.cos(theta) * p + np.sin(theta) * \
                (np.cross(e, p)) + (1 - np.cos(theta)) * np.dot(e, p) * e
            pts_rotated[i] = p_rotated
    return pts_rotated

'''
def circle_profile(origin: gp_Pnt, direction: gp_Vec, radius: float) -> TopoDS_Face:
    circle = gp_Circ(gp_Ax2(origin, direction), radius)
    edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return BRepBuilderAPI_MakeFace(wire).Face()
'''
def add_point_and_vector(p1: gp_Pnt, v1: gp_Vec) -> gp_Pnt:
    return gp_Pnt(
        p1.X() + v1.X(),
        p1.Y() + v1.Y(),
        p1.Z() + v1.Z())


MAX_THETA_DEGREES = 89  # exactly 90 leaves the last pipe flat, which rounded_channel's sphere fuse cannot build
ARC_STEP_DEGREES = 10  # a bend is cut into pipes this many degrees long, small enough to read as a curve


class CustomNeedleError(ValueError):
    """A custom needle's numbers break a rule. The text is written for the clinician who typed them."""


@dataclass(frozen=True)
class CustomNeedleSpec:
    """What a user types to add a needle. Lengths, radius, x and y are mm, theta and phi degrees.

    x and y are the start on the cylinder's base. After Length 1 the needle turns by theta from
    the axis towards phi, measured from +X towards +Y, along an arc of the given radius.
    """
    label: str
    x: float
    y: float
    length1: float
    length2: float
    radius: float = 0.0
    theta: float = 0.0
    phi: float = 0.0


def custom_needle_points(
    spec: CustomNeedleSpec, cylinder_diameter: float, cylinder_length: float, needle_diameter: float
) -> list[list[float]]:
    """Turn a spec into the points of a DICOM channel, tissue end first, in cylinder coordinates.

    The path runs straight up from the base start for Length 1, then turns by theta along an
    arc, sampled every ARC_STEP_DEGREES, and goes on for Length 2 in the new direction. The start
    is at most the cylinder radius less the needle's radius from the axis, so the straight run
    stays inside. A broken rule raises CustomNeedleError.
    """
    numbers = (spec.x, spec.y, spec.length1, spec.length2, spec.radius, spec.theta, spec.phi)
    if not all(math.isfinite(value) for value in numbers):
        raise CustomNeedleError("Every value must be a number")
    if spec.length1 <= 0:
        raise CustomNeedleError("Length 1 must be above 0 mm")
    if spec.length2 <= 0:
        raise CustomNeedleError("Length 2 must be above 0 mm")
    if spec.length1 > cylinder_length:
        raise CustomNeedleError(f"Length 1 must be at most the cylinder length of {cylinder_length:g} mm")
    limit = (cylinder_diameter - needle_diameter) / 2
    if math.hypot(spec.x, spec.y) > limit:
        raise CustomNeedleError(f"The start must be within {limit:g} mm of the centre of the base so the whole needle stays inside the cylinder")
    if not 0 <= spec.theta <= MAX_THETA_DEGREES:
        raise CustomNeedleError(f"Theta must be between 0 and {MAX_THETA_DEGREES} degrees")
    if spec.theta > 0 and spec.radius <= 0:
        raise CustomNeedleError("A bend needs a radius above 0 mm")
    if spec.theta == 0:
        return [[spec.x, spec.y, spec.length1 + spec.length2], [spec.x, spec.y, 0.0]]
    direction = (math.cos(math.radians(spec.phi)), math.sin(math.radians(spec.phi)))
    steps = math.ceil(spec.theta / ARC_STEP_DEGREES)
    arc = []
    for step in range(steps + 1):
        angle = math.radians(spec.theta * step / steps)
        sideways = spec.radius * (1 - math.cos(angle))
        arc.append([spec.x + sideways * direction[0], spec.y + sideways * direction[1], spec.length1 + spec.radius * math.sin(angle)])
    turn = math.radians(spec.theta)
    tip = [arc[-1][0] + spec.length2 * math.sin(turn) * direction[0], arc[-1][1] + spec.length2 * math.sin(turn) * direction[1],
           arc[-1][2] + spec.length2 * math.cos(turn)]
    return [tip, *reversed(arc), [spec.x, spec.y, 0.0]]
