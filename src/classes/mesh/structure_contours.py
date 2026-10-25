"""Read-only DICOM contour outlines aligned with the probe, never export solids."""
from dataclasses import dataclass
from math import isfinite

import numpy as np
from numpy.typing import NDArray
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.gp import gp_Pnt

from classes.dicom.structures import Contour

Point = tuple[float, float, float]


@dataclass(frozen=True)
class ContourAlignment:
    """The same patient-to-cylinder reference used when importing needle paths."""
    base: Point
    direction: Point
    length: float
    frame_uid: str

    def __post_init__(self):
        if not self.frame_uid or not all(isfinite(v) for v in (*self.base, *self.direction, self.length)):
            raise ValueError('Missing or invalid contour alignment')
        direction = np.asarray(self.direction)
        if np.linalg.norm(direction) == 0 or self.length <= 0:
            raise ValueError('A positive probe length and nonzero axis are required')
        if direction[0] == direction[1] == 0 and direction[2] < 0:
            raise ValueError('The needle importer does not support a reversed Z axis')


def transform_contour(contour: Contour, alignment: ContourAlignment) -> Contour:
    """Rotate around the probe base and preserve its tip at the current length."""
    points = transform_points(np.asarray(contour.points), alignment)
    return Contour(contour.geometric_type, tuple((float(x), float(y), float(z)) for x, y, z in points))


def transform_points(vertices: NDArray[np.float64], alignment: ContourAlignment) -> NDArray[np.float64]:
    """Align patient vertices without modifying the cached source coordinates."""
    direction = np.asarray(alignment.direction)
    axis_length = np.linalg.norm(direction)
    source = direction / axis_length
    target = np.array((0., 0., 1.))
    points = vertices - np.asarray(alignment.base)
    cross = np.cross(source, target)
    sine = np.linalg.norm(cross)
    if sine:
        axis = cross / sine
        cosine = np.clip(np.dot(source, target), -1., 1.)
        points = points * cosine + np.cross(axis, points) * sine + np.outer(points @ axis, axis) * (1 - cosine)
    points[:, 2] += alignment.length - axis_length
    return points


def contour_outline(contours: tuple[Contour, ...]) -> TopoDS_Compound:
    """Keep each closed contour separate, including XOR boundaries and holes."""
    builder = BRep_Builder()
    result = TopoDS_Compound()
    builder.MakeCompound(result)
    for contour in contours:
        if contour.geometric_type not in ('CLOSED_PLANAR', 'CLOSEDPLANAR_XOR'):
            raise ValueError('Only closed contour outlines are supported')
        points = []
        for point in contour.points:
            if not points or point != points[-1]:
                points.append(point)
        if len(points) > 1 and points[0] == points[-1]:
            points.pop()
        if len(set(points)) < 3:
            raise ValueError('A contour needs three distinct points')
        polygon = BRepBuilderAPI_MakePolygon()
        for point in points:
            polygon.Add(gp_Pnt(*point))
        polygon.Close()
        if not polygon.IsDone():
            raise ValueError('The contour outline could not be built')
        builder.Add(result, polygon.Wire())
    return result
