"""Revision-tagged organ checks and temporary needle emphasis, separate from exports."""
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot

from classes.app import get_app
from classes.logger import log
from classes.mesh.channel import apply_deadspace_to_points
from classes.mesh.needle_collisions import CollisionSurface, NeedlePath
from classes.mesh.structure_contours import ContourAlignment, transform_points
from classes.mesh.structure_surfaces import AnatomySurface
from windows.models.channels_model import ChannelsModel
from windows.models.structures_model import StructuresModel


@dataclass(frozen=True)
class CollisionResult:
    revision: int
    collisions: dict[int, tuple[str, ...]]
    errors: dict[int, str] = field(default_factory=dict)
    indexes: dict[int, CollisionSurface] = field(default_factory=dict)


class CollisionSignals(QObject):
    finished = Signal(object)


class CollisionTask(QRunnable):
    def __init__(self, revision: int, surfaces: dict[int, AnatomySurface],
                 alignment: ContourAlignment, needles: tuple[NeedlePath, ...],
                 indexes: dict[int, CollisionSurface]):
        super().__init__()
        self.revision = revision
        self.surfaces = surfaces
        self.alignment = alignment
        self.needles = needles
        self.signals = CollisionSignals()
        self.indexes = indexes.copy()

    def run(self):
        collisions: dict[int, tuple[str, ...]] = {}
        errors: dict[int, str] = {}
        for roi, surface in self.surfaces.items():
            try:
                if roi not in self.indexes:
                    aligned = AnatomySurface(transform_points(surface.vertices, self.alignment), surface.triangles)
                    self.indexes[roi] = CollisionSurface(aligned)
                indexed = self.indexes[roi]
                hits = tuple(needle.label for needle in self.needles if indexed.intersects(needle))
                if hits:
                    collisions[roi] = hits
            except Exception:
                log.exception('Organ collision mesh could not be checked')
                errors[roi] = 'Organ geometry could not be checked. Inspect the contours.'
        self.signals.finished.emit(CollisionResult(self.revision, collisions, errors, self.indexes))


class CollisionModel(QObject):
    changed = Signal()
    highlight_changed = Signal()

    def __init__(self, structures: StructuresModel, channels: ChannelsModel):
        super().__init__()
        self.structures = structures
        self.channels = channels
        self.collisions: dict[int, tuple[str, ...]] = {}
        self.unchecked: dict[int, str] = {}
        self.highlighted: tuple[str, ...] = ()
        self.revision = 0
        self.busy = False
        self.indexes: dict[int, CollisionSurface] = {}
        self._anatomy = None
        self._needles: tuple[NeedlePath, ...] | None = None
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self.check)
        structures.changed.connect(self.invalidate)
        channels.values_changed.connect(self.invalidate)

    def paths(self) -> tuple[NeedlePath, ...]:
        deadspace = float(get_app().values.config_values['CONFIG_DEADSPACE'])
        paths = []
        for channel in self.channels.get_visible_channels():
            points = tuple(tuple(float(v) for v in point) for point in
                           apply_deadspace_to_points(channel.get_points(), deadspace))
            if points and points[-1][2] >= 0:
                x, y, _ = points[-1]
                points += ((x, y, -1.),)
            paths.append(NeedlePath(channel.label, points, channel.get_diameter() / 2))
        return tuple(paths)

    def invalidate(self):
        """Ignore display-only changes; clear stale results when check inputs change."""
        surfaces, unchecked = self.structures.prepare_organ_collision_surfaces(request_missing=False)
        anatomy = (tuple(self.structures.structures.values()), self.structures.alignment,
                   tuple((roi, id(surface)) for roi, surface in surfaces.items()), tuple(unchecked.items()))
        try:
            needles = self.paths()
        except Exception:
            needles = None  # check() logs the failure and reports every affected organ unchecked.
        if anatomy == self._anatomy and needles == self._needles:
            return
        if anatomy != self._anatomy:
            self.indexes.clear()
        self._anatomy, self._needles = anatomy, needles
        self.revision += 1
        self.pool.clear()
        self.collisions.clear()
        self.unchecked.clear()
        self.highlight(None)
        self.busy = bool(self.structures.structures and self.channels.channels)
        self.changed.emit()
        self.timer.start()

    def check(self):
        surfaces, unchecked = self.structures.prepare_organ_collision_surfaces()
        self.unchecked = unchecked
        self.busy = False
        try:
            needles = self.paths()
        except Exception:
            log.exception('Needle geometry could not be checked')
            self.collisions.clear()
            self.highlight(None)
            self.unchecked.update({roi: 'Needle geometry could not be checked. Review the needle settings.'
                                   for roi in surfaces})
            self.changed.emit()
            return
        if not needles or not surfaces or self.structures.alignment is None:
            self.changed.emit()
            return
        self.busy = True
        task = CollisionTask(self.revision, surfaces, self.structures.alignment, needles, self.indexes)
        task.signals.finished.connect(self.accept)
        self.pool.start(task)
        self.changed.emit()

    @Slot(object)
    def accept(self, result: CollisionResult):
        if result.revision != self.revision:
            return
        self.busy = False
        self.indexes = result.indexes
        self.collisions = result.collisions
        self.unchecked.update(result.errors)
        self.changed.emit()

    def highlight(self, roi: int | None):
        highlighted = self.collisions.get(roi, ())
        if highlighted != self.highlighted:
            self.highlighted = highlighted
            self.highlight_changed.emit()
