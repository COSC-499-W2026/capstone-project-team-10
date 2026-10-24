"""Display-only anatomy state; contour outlines never enter printable geometry."""
from dataclasses import dataclass, replace

from OCC.Core.TopoDS import TopoDS_Compound
from PySide6.QtCore import QObject, Signal

from classes.dicom.data import DicomData
from classes.dicom.structures import Structure, StructureType
from classes.mesh.structure_contours import ContourAlignment, contour_outline, transform_contour


@dataclass(frozen=True)
class StructurePresentation:
    roi_number: int
    color: tuple[int, int, int]
    outline: TopoDS_Compound


class StructuresModel(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.structures: dict[int, Structure] = {}
        self.visible: set[int] = set()
        self.unavailable: dict[int, str] = {}
        self.alignment: ContourAlignment | None = None
        self._outlines: dict[int, StructurePresentation] = {}

    def clear(self):
        self.structures.clear()
        self.visible.clear()
        self.unavailable.clear()
        self._outlines.clear()
        self.alignment = None
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
        try:
            contours = tuple(transform_contour(c, self.alignment) for c in structure.contours)
            self._outlines[roi] = StructurePresentation(roi, structure.color, contour_outline(contours))
            self.visible.add(roi)
        except (ValueError, RuntimeError) as error:
            self.unavailable[roi] = f'Outline unavailable. {error}'
            self.visible.discard(roi)

    def set_visible(self, roi: int, visible: bool):
        if roi not in self.structures or roi in self.unavailable:
            raise ValueError('This structure is unavailable')
        if visible:
            if roi in self._outlines:
                self.visible.add(roi)
            else:
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
