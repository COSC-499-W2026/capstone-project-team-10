"""Conservative needle-capsule checks against closed, approximate organ meshes."""
from dataclasses import dataclass
from math import ceil, isfinite

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import cKDTree

from classes.mesh.structure_contours import Point
from classes.mesh.structure_surfaces import AnatomySurface


@dataclass(frozen=True)
class NeedlePath:
    label: str
    points: tuple[Point, ...]
    radius: float

    def __post_init__(self):
        if (len(self.points) < 2 or not isfinite(self.radius) or self.radius <= 0
                or any(len(point) != 3 or not all(isfinite(v) for v in point) for point in self.points)):
            raise ValueError('Needle collision checks require finite paths and a positive radius')


def triangle_distances(point: NDArray[np.float64], triangles: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return distances to triangle interiors or their closest boundary edges."""
    a, b, c = np.moveaxis(triangles, 1, 0)
    ab, ac, ap = b - a, c - a, point - a
    normal = np.cross(ab, ac)
    squared_normal = np.einsum('ij,ij->i', normal, normal)
    signed = np.einsum('ij,ij->i', ap, normal)
    projection = ap - normal * (signed / squared_normal)[:, None]
    u = np.einsum('ij,ij->i', np.cross(projection, ac), normal) / squared_normal
    v = np.einsum('ij,ij->i', np.cross(ab, projection), normal) / squared_normal
    distances = np.where((u >= 0) & (v >= 0) & (u + v <= 1),
                         np.abs(signed) / np.sqrt(squared_normal), np.inf)
    for start, end in ((a, b), (b, c), (c, a)):
        edge = end - start
        t = np.clip(np.einsum('ij,ij->i', point - start, edge)
                    / np.einsum('ij,ij->i', edge, edge), 0., 1.)
        distances = np.minimum(distances, np.linalg.norm(point - start - t[:, None] * edge, axis=1))
    return distances


class CollisionSurface:
    """Cache a triangle index; the closed surface must have consistent winding."""

    def __init__(self, surface: AnatomySurface):
        self.triangles = surface.vertices[surface.triangles]
        if not len(self.triangles) or not np.isfinite(self.triangles).all():
            raise ValueError('Organ collision mesh is empty or nonfinite')
        normals = np.cross(self.triangles[:, 1] - self.triangles[:, 0],
                           self.triangles[:, 2] - self.triangles[:, 0])
        if np.any(np.linalg.norm(normals, axis=1) == 0):
            raise ValueError('Organ collision mesh contains degenerate triangles')
        centres = self.triangles.mean(axis=1)
        self.tree = cKDTree(centres)
        self.reach = float(np.linalg.norm(self.triangles - centres[:, None, :], axis=2).max())
        self.lower = self.triangles.min(axis=(0, 1))
        self.upper = self.triangles.max(axis=(0, 1))

    def contains(self, point: NDArray[np.float64]) -> bool:
        """Use signed solid angles so enclosed needles and XOR cavities are distinguished."""
        if np.any(point < self.lower) or np.any(point > self.upper):
            return False
        a, b, c = np.moveaxis(self.triangles - point, 1, 0)
        la, lb, lc = (np.linalg.norm(vertex, axis=1) for vertex in (a, b, c))
        numerator = np.einsum('ij,ij->i', a, np.cross(b, c))
        denominator = (la * lb * lc + np.einsum('ij,ij->i', a, b) * lc
                       + np.einsum('ij,ij->i', b, c) * la + np.einsum('ij,ij->i', c, a) * lb)
        return bool(abs(np.arctan2(numerator, denominator).sum()) > np.pi)

    def intersects(self, needle: NeedlePath) -> bool:
        """Check the full polyline with radius and a conservative 0.25 mm sampling allowance.

        Samples are at most 0.5 mm apart: expanding by half that spacing avoids
        skipping a crossing between samples. This is not a clinical clearance margin.
        """
        points = np.asarray(needle.points, dtype=float)
        radius = needle.radius + 0.25
        if np.any(points.max(axis=0) + radius < self.lower) or np.any(points.min(axis=0) - radius > self.upper):
            return False
        if self.contains(points[0]):
            return True
        for start, end in zip(points[:-1], points[1:]):
            count = max(1, ceil(float(np.linalg.norm(end - start)) / 0.5))
            for offset in range(0, count + 1, 512):
                steps = np.arange(offset, min(offset + 512, count + 1)) / count
                samples = start + steps[:, None] * (end - start)
                neighbours = self.tree.query_ball_point(samples, self.reach + radius)
                for point, indices in zip(samples, neighbours):
                    if indices and np.any(triangle_distances(point, self.triangles[indices]) <= radius):
                        return True
        return False
