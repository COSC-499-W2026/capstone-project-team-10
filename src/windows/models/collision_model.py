"""Revision-tagged organ checks and temporary needle emphasis, separate from exports."""
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot

from classes.app import get_app
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


class CollisionSignals(QObject):
    finished = Signal(object)


class CollisionTask(QRunnable):
    def __init__(self, revision: int, surfaces: dict[int, AnatomySurface],
                 alignment: ContourAlignment, needles: tuple[NeedlePath, ...]):
        super().__init__()
        self.revision = revision
        self.surfaces = surfaces
        self.alignment = alignment
        self.needles = needles
        self.signals = CollisionSignals()

    def run(self):
        collisions: dict[int, tuple[str, ...]] = {}
        errors: dict[int, str] = {}
        for roi, surface in self.surfaces.items():
            try:
                aligned = AnatomySurface(transform_points(surface.vertices, self.alignment), surface.triangles)
                indexed = CollisionSurface(aligned)
                hits = tuple(needle.label for needle in self.needles if indexed.intersects(needle))
                if hits:
                    collisions[roi] = hits
            except Exception as error:
                errors[roi] = f'Collision check unavailable: {error}'
        self.signals.finished.emit(CollisionResult(self.revision, collisions, errors))


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
        """Clear stale red emphasis immediately; debounce geometry checks."""
        self.revision += 1
        self.pool.clear()
        self.collisions.clear()
        self.unchecked.clear()
        self.highlight(None)
        self.busy = bool(self.structures.structures and self.channels.channels)
        self.changed.emit()
        self.timer.start()

    def check(self):
        surfaces, unchecked = self.structures.organ_collision_surfaces()
        self.unchecked = unchecked
        self.busy = False
        try:
            needles = self.paths()
        except ValueError as error:
            self.unchecked.update({roi: str(error) for roi in surfaces})
            self.changed.emit()
            return
        if not needles or not surfaces or self.structures.alignment is None:
            self.changed.emit()
            return
        self.busy = True
        task = CollisionTask(self.revision, surfaces, self.structures.alignment, needles)
        task.signals.finished.connect(self.accept)
        self.pool.start(task)
        self.changed.emit()

    @Slot(object)
    def accept(self, result: CollisionResult):
        if result.revision != self.revision:
            return
        self.busy = False
        self.collisions = result.collisions
        self.unchecked.update(result.errors)
        self.changed.emit()

    def highlight(self, roi: int | None):
        self.highlighted = self.collisions.get(roi, ())
        self.highlight_changed.emit()
