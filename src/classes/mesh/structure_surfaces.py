"""Approximate display surfaces from parallel axial DICOM contour slices."""
from dataclasses import dataclass
from OCC.Core.Poly import Poly_Triangulation
from classes.mesh.structure_contours import ContourAlignment, transform_points

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import distance_transform_edt
from skimage.draw import polygon2mask
from skimage.measure import marching_cubes

from classes.dicom.structures import Contour


@dataclass(frozen=True)
class SampledAnatomy:
    values: NDArray[np.float32]
    origin: NDArray[np.float64]
    spacing: float


@dataclass(frozen=True)
class AnatomySurface:
    vertices: NDArray[np.float64]
    triangles: NDArray[np.int32]


def axial_slices(contours: tuple[Contour, ...]) -> dict[float, list[Contour]]:
    """Group axial loops without silently flattening oblique or nonplanar contours."""
    slices: dict[float, list[Contour]] = {}
    kinds = {contour.geometric_type for contour in contours}
    if not kinds or not kinds <= {'CLOSED_PLANAR', 'CLOSEDPLANAR_XOR'} or len(kinds) != 1:
        raise ValueError('Surface preview requires closed contours of one geometric type')
    for contour in contours:
        points = np.asarray(contour.points)
        if len(points) < 3 or not np.isfinite(points).all():
            raise ValueError('Surface preview requires finite closed polygons')
        if np.ptp(points[:, 2]) > 0.01:
            raise ValueError('Surface preview currently supports patient-axial slices only')
        height = round(float(np.mean(points[:, 2])), 2)
        slices.setdefault(height, []).append(contour)
    heights = np.array(sorted(slices))
    if len(heights) < 2:
        raise ValueError('At least two contour slices are needed for a surface')
    intervals = np.diff(heights)
    if intervals.max() > 2.5 * intervals.min():
        raise ValueError('Large gaps between contour slices; use outlines to inspect them')
    return slices


def slice_field(contours: list[Contour], origin: NDArray[np.float64], spacing: float,
                dimensions: tuple[int, int]) -> NDArray[np.float32]:
    """Rasterize union or XOR semantics and retain separate regions and holes."""
    inside = np.zeros(dimensions, dtype=bool)
    for contour in contours:
        polygon = (np.asarray(contour.points)[:, :2] - origin[:2]) / spacing
        mask = polygon2mask(dimensions, polygon)
        if contour.geometric_type == 'CLOSEDPLANAR_XOR':
            inside ^= mask
        else:
            inside |= mask
    if not inside.any():
        raise ValueError('Contours are too small for the surface preview resolution')
    return np.asarray((distance_transform_edt(inside) - distance_transform_edt(~inside)) * spacing,
                      dtype=np.float32)


def sample_contours(contours: tuple[Contour, ...], spacing: float = 1.) -> SampledAnatomy:
    """Sample signed slice distances in patient mm, with bounded memory use."""
    if not np.isfinite(spacing) or spacing <= 0:
        raise ValueError('Surface spacing must be positive and finite')
    slices = axial_slices(contours)
    points = np.concatenate([np.asarray(contour.points) for contour in contours])
    origin = points.min(axis=0) - spacing * 2
    dimensions = np.ceil((points.max(axis=0) - origin) / spacing).astype(int) + 3
    field_cells = float(dimensions[0]) * float(dimensions[1]) * len(slices)
    if np.prod(dimensions.astype(float)) + field_cells > 32_000_000:
        raise ValueError('Structure exceeds the surface preview size limit; use outlines')
    nx, ny, nz = (int(dimension) for dimension in dimensions)
    heights = np.array(sorted(slices))
    fields = [slice_field(slices[height], origin, spacing, (nx, ny)) for height in heights]
    volume = np.empty((nx, ny, nz), dtype=np.float32)
    for index in range(nz):
        height = origin[2] + index * spacing
        if height < heights[0]:
            volume[:, :, index] = -np.abs(fields[0])
        elif height > heights[-1]:
            volume[:, :, index] = -np.abs(fields[-1])
        else:
            upper = min(int(np.searchsorted(heights, height, side='right')), len(heights) - 1)
            lower = max(upper - 1, 0)
            weight = (height - heights[lower]) / (heights[upper] - heights[lower])
            volume[:, :, index] = fields[lower] * (1 - weight) + fields[upper] * weight
    return SampledAnatomy(volume, origin, spacing)


def reconstruct_surface(contours: tuple[Contour, ...], spacing: float = 1.) -> AnatomySurface:
    """Extract a closed preview mesh; sampled detail is not additional clinical data."""
    volume = sample_contours(contours, spacing)
    vertices, triangles, _, _ = marching_cubes(volume.values, level=0.,
                                              spacing=(spacing, spacing, spacing),
                                              allow_degenerate=False)
    return AnatomySurface(np.asarray(vertices + volume.origin, dtype=np.float64),
                          np.asarray(triangles, dtype=np.int32))


def surface_triangulation(surface: AnatomySurface, alignment: ContourAlignment) -> Poly_Triangulation:
    """Align patient vertices and compute smooth display normals in OpenCASCADE."""
    from OCC.Core.Poly import Poly_Triangle, Poly_Triangulation
    from OCC.Core.gp import gp_Pnt
    aligned = transform_points(surface.vertices, alignment)
    mesh = Poly_Triangulation(len(aligned), len(surface.triangles), False)
    for index, point in enumerate(aligned, 1):
        mesh.SetNode(index, gp_Pnt(*point))
    for index, triangle in enumerate(surface.triangles, 1):
        mesh.SetTriangle(index, Poly_Triangle(*(int(vertex) + 1 for vertex in triangle)))
    mesh.ComputeNormals()
    return mesh
