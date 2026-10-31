"""Display-only anatomy state; outlines and surfaces never enter printable geometry."""
from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass, replace
from enum import Enum
from math import isfinite
from OCC.Core.Poly import Poly_Triangulation
if TYPE_CHECKING:
    from classes.mesh.structure_surfaces import AnatomySurface

from OCC.Core.TopoDS import TopoDS_Compound
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

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


@dataclass(frozen=True)
class SurfaceResult:
    generation: int
    roi: int
    alignment: ContourAlignment
    sampled: AnatomySurface | None = None
    mesh: Poly_Triangulation | None = None
    error: str = ''


class SurfaceSignals(QObject):
    finished = Signal(object)


class SurfaceTask(QRunnable):
    """Build private mesh values off the GUI thread; never touch viewer actors."""

    def __init__(self, generation: int, structure: Structure, alignment: ContourAlignment,
                 sampled: AnatomySurface | None):
        super().__init__()
        self.generation = generation
        self.structure = structure
        self.alignment = alignment
        self.sampled = sampled
        self.signals = SurfaceSignals()

    def reconstruct(self) -> AnatomySurface:
        """Sample this ROI when no cached patient-space surface is available."""
        from classes.mesh.structure_surfaces import reconstruct_surface
        spacing = 2. if self.structure.interpreted_type == 'EXTERNAL' else 1.
        return reconstruct_surface(self.structure.contours, spacing=spacing)

    def run(self):
        result = SurfaceResult(self.generation, self.structure.roi_number, self.alignment)
        try:
            from classes.mesh.structure_surfaces import surface_triangulation
            sampled = self.sampled
            if sampled is None:
                sampled = self.reconstruct()
            result = replace(result, sampled=sampled,
                             mesh=surface_triangulation(sampled, self.alignment))
        except ImportError:
            result = replace(result, error='Install scipy and scikit-image to enable surface previews')
        except (ValueError, RuntimeError) as error:
            result = replace(result, error=str(error))
        except Exception as error:
            result = replace(result, error=f'Surface reconstruction failed. {error}')
        self.signals.finished.emit(result)


class StructuresModel(QObject):
    changed = Signal()
    opacity_changed = Signal(int, float)
    highlight_changed = Signal()

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
        self._opacities: dict[int, float] = {}
        self.outline_errors: dict[int, str] = {}
        self.pending: set[int] = set()
        self.highlighted: int | None = None
        self._generation = 0
        self.surface_pool = QThreadPool(self)
        self.surface_pool.setMaxThreadCount(1)

    def clear(self):
        self._generation += 1
        self.surface_pool.clear()
        self.pending.clear()
        self.outline_errors.clear()
        self._opacities.clear()
        self.structures.clear()
        self.visible.clear()
        self.unavailable.clear()
        self._outlines.clear()
        self.alignment = None
        self._surfaces.clear()
        self.surface_errors.clear()
        self.highlighted = None
        self.changed.emit()

    def load_plan(self, plan: DicomData, length: float):
        self.clear()
        self.structures = {roi.roi_number: roi for roi in plan.structures or ()}
        try:
            if not plan.probe_frame_uid or plan.cylinder_base is None or plan.cylinder_direction is None:
                raise ValueError('No probe frame is available for alignment')
            base = tuple(float(v) for v in plan.cylinder_base)
            direction = tuple(float(v) for v in plan.cylinder_direction)
            if len(base) != 3 or len(direction) != 3:
                raise ValueError('Probe coordinates need three components')
            self.alignment = ContourAlignment(base, direction, length, plan.probe_frame_uid)
        except ValueError as error:
            self.unavailable = {roi: str(error) for roi in self.structures}
            self.changed.emit()
            return
        for roi, structure in self.structures.items():
            if structure.frame_of_reference_uid != plan.probe_frame_uid:
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
        if roi not in self._outlines:
            self._outlines[roi] = StructurePresentation(roi, structure.color)
        if (self.mode != StructureDisplayMode.SURFACE and self._outlines[roi].outline is None
                and roi not in self.outline_errors):
            try:
                contours = tuple(transform_contour(c, self.alignment) for c in structure.contours)
                self._outlines[roi] = replace(self._outlines[roi], outline=contour_outline(contours))
            except (ValueError, RuntimeError) as error:
                self.outline_errors[roi] = str(error)
        if self.mode != StructureDisplayMode.OUTLINES and self._outlines[roi].surface is None:
            self._attach_surface(roi)
        self.visible.add(roi)

    def _attach_surface(self, roi: int):
        if self.alignment is None or roi in self.surface_errors or roi in self.pending:
            return
        self.pending.add(roi)
        task = SurfaceTask(self._generation, self.structures[roi], self.alignment, self._surfaces.get(roi))
        task.signals.finished.connect(self._accept_surface)
        self.surface_pool.start(task)

    @Slot(object)
    def _accept_surface(self, result: SurfaceResult):
        if result.generation != self._generation:
            return
        roi = result.roi
        self.pending.discard(roi)
        if result.error:
            self.surface_errors[roi] = result.error
        else:
            self._surfaces[roi] = result.sampled
            if result.alignment == self.alignment and roi in self._outlines:
                self._outlines[roi] = replace(self._outlines[roi], surface=result.mesh)
            elif roi in self.visible and self.mode != StructureDisplayMode.OUTLINES:
                self._attach_surface(roi)
        self.changed.emit()

    def status_message(self, roi: int) -> str:
        if roi in self.unavailable:
            return self.unavailable[roi]
        reasons = []
        if self.mode != StructureDisplayMode.OUTLINES:
            if roi in self.pending:
                reasons.append('Building surface…')
            elif roi in self.surface_errors:
                reasons.append(f'Surface unavailable. {self.surface_errors[roi]}')
        if self.mode != StructureDisplayMode.SURFACE and roi in self.outline_errors:
            reasons.append(f'Outline unavailable. {self.outline_errors[roi]}')
        return '\n'.join(reasons)

    def is_displayed(self, roi: int) -> bool:
        presentation = self._outlines.get(roi)
        return roi in self.visible and presentation is not None and (
            (self.mode != StructureDisplayMode.OUTLINES and presentation.surface is not None)
            or (self.mode != StructureDisplayMode.SURFACE and presentation.outline is not None))

    def set_mode(self, mode: StructureDisplayMode):
        self.mode = mode
        for roi in tuple(self.visible):
            self._enable(roi)
        self.changed.emit()

    def opacity_for(self, roi: int) -> float:
        return self._opacities.get(roi, 0.45)

    def set_opacity(self, roi: int, opacity: float):
        if roi not in self.structures:
            raise ValueError('This structure is unavailable')
        if not isfinite(opacity) or not 0 <= opacity <= 1:
            raise ValueError('Opacity must be between zero and one')
        self._opacities[roi] = opacity
        self.opacity_changed.emit(roi, opacity)

    def set_highlight(self, roi: int | None):
        """Remember which listed structure the viewport should emphasise.

        Passing None clears it. This does not create geometry, so a row with no
        contour stays listed and is not added to the preview.
        """
        if roi is not None and roi not in self.structures:
            raise ValueError('This structure is unavailable')
        self.highlighted = roi
        self.highlight_changed.emit()

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
