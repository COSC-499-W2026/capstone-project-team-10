"""Display-only anatomy state; outlines and surfaces never enter printable geometry."""
from dataclasses import dataclass, replace
from enum import Enum
from math import isfinite
from OCC.Core.Poly import Poly_Triangulation
from classes.mesh.structure_surfaces import AnatomySurface, reconstruct_surface, surface_triangulation

from OCC.Core.TopoDS import TopoDS_Compound
from PySide6.QtCore import QObject, Signal

from classes.dicom.data import DicomData
from classes.dicom.structures import Structure, StructureType
from classes.mesh.structure_contours import ContourAlignment, contour_outline, transform_contour


class StructureDisplayMode(Enum):
    OUTLINES = 'Outlines'
    SURFACE = 'Surface'
    BOTH = 'Both'


@dataclass(frozen=True)
class StructurePresentation:
    roi_number: int
    color: tuple[int, int, int]
    outline: TopoDS_Compound | None = None
    surface: Poly_Triangulation | None = None


class StructuresModel(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.structures: dict[int, Structure] = {}
        self.visible: set[int] = set()
        self.unavailable: dict[int, str] = {}
        self.alignment: ContourAlignment | None = None
        self._outlines: dict[int, StructurePresentation] = {}
        self._surfaces: dict[int, AnatomySurface] = {}
        self.surface_errors: dict[int, str] = {}
        self.mode = StructureDisplayMode.SURFACE
        self.opacity = 0.45

    def clear(self):
        self.structures.clear()
        self.visible.clear()
        self.unavailable.clear()
        self._outlines.clear()
        self.alignment = None
        self._surfaces.clear()
        self.surface_errors.clear()
        self.changed.emit()

    def load_plan(self, plan: DicomData, length: float):
        self.clear()
        self.structures = {roi.roi_number: roi for roi in plan.structures or ()}
        reference = self.structures.get(plan.central_channel_roi) or self.structures.get(plan.cylinder_roi)
        try:
            if reference is None or plan.cylinder_base is None or plan.cylinder_direction is None:
                raise ValueError('No probe frame is available for alignment')
            base = tuple(float(v) for v in plan.cylinder_base)
            direction = tuple(float(v) for v in plan.cylinder_direction)
            if len(base) != 3 or len(direction) != 3:
                raise ValueError('Probe coordinates need three components')
            self.alignment = ContourAlignment(base, direction, length, reference.frame_of_reference_uid)
        except ValueError as error:
            self.unavailable = {roi: str(error) for roi in self.structures}
            self.changed.emit()
            return
        for roi, structure in self.structures.items():
            if structure.frame_of_reference_uid != reference.frame_of_reference_uid:
                self.unavailable[roi] = 'Different frame of reference from the probe'
            elif not structure.contours:
                self.unavailable[roi] = 'No contour geometry'
            elif any(c.geometric_type not in ('CLOSED_PLANAR', 'CLOSEDPLANAR_XOR') for c in structure.contours):
                self.unavailable[roi] = 'Only closed contour outlines are supported'
            elif structure.category in (StructureType.ORGAN, StructureType.TUMOUR):
                self._enable(roi)
        self.changed.emit()

    def _enable(self, roi: int):
        if self.alignment is None:
            return
        structure = self.structures[roi]
        try:
            if roi not in self._outlines:
                self._outlines[roi] = StructurePresentation(roi, structure.color)
            if self.mode != StructureDisplayMode.SURFACE and self._outlines[roi].outline is None:
                contours = tuple(transform_contour(c, self.alignment) for c in structure.contours)
                self._outlines[roi] = replace(self._outlines[roi], outline=contour_outline(contours))
            if self.mode != StructureDisplayMode.OUTLINES and self._outlines[roi].surface is None:
                self._attach_surface(roi)
            self.visible.add(roi)
        except (ValueError, RuntimeError) as error:
            self.unavailable[roi] = f'Outline unavailable: {error}'
            self.visible.discard(roi)

    def _attach_surface(self, roi: int):
        if self.alignment is None or roi in self.surface_errors:
            return
        try:
            if roi not in self._surfaces:
                structure = self.structures[roi]
                spacing = 2. if structure.interpreted_type == 'EXTERNAL' else 1.
                self._surfaces[roi] = reconstruct_surface(structure.contours, spacing=spacing)
            mesh = surface_triangulation(self._surfaces[roi], self.alignment)
            self._outlines[roi] = replace(self._outlines[roi], surface=mesh)
        except (ValueError, RuntimeError) as error:
            self.surface_errors[roi] = str(error)

    def set_mode(self, mode: StructureDisplayMode):
        self.mode = mode
        for roi in tuple(self.visible):
            self._enable(roi)
        self.changed.emit()

    def set_opacity(self, opacity: float):
        if not isfinite(opacity) or not 0 <= opacity <= 1:
            raise ValueError('Opacity must be between zero and one')
        self.opacity = opacity
        self.changed.emit()

    def set_visible(self, roi: int, visible: bool):
        if roi not in self.structures or roi in self.unavailable:
            raise ValueError('This structure is unavailable')
        if visible:
            self._enable(roi)
        else:
            self.visible.discard(roi)
        self.changed.emit()

    def set_length(self, length: float):
        if self.alignment is None or self.alignment.length == length:
            return
        self.alignment = replace(self.alignment, length=length)
        selected = tuple(self.visible)
        self._outlines.clear()
        for roi in selected:
            self._enable(roi)
        self.changed.emit()

    def presentations(self) -> tuple[StructurePresentation, ...]:
        return tuple(self._outlines[roi] for roi in sorted(self.visible))
