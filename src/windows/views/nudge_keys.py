"""Alt (Option on a Mac) with an arrow or Page key nudges the selected applicator in the plan's X, Y and Z."""
from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt

from classes.mesh.channel import Translation
from windows.views.add_applicator_dialog import RANGE_MM

STEP_MM = 1.0
FINE_STEP_MM = 0.1  # with Shift held

AXIS_KEYS = {
    Qt.Key.Key_Left: (-1.0, 0.0, 0.0),
    Qt.Key.Key_Right: (1.0, 0.0, 0.0),
    Qt.Key.Key_Up: (0.0, 1.0, 0.0),
    Qt.Key.Key_Down: (0.0, -1.0, 0.0),
    Qt.Key.Key_PageUp: (0.0, 0.0, 1.0),
    Qt.Key.Key_PageDown: (0.0, 0.0, -1.0),
}
# Page Up and Down need Fn on a Mac laptop, so Ctrl (Cmd on a Mac) turns Up and Down into Z
CTRL_AXIS_KEYS = {
    Qt.Key.Key_Up: (0.0, 0.0, 1.0),
    Qt.Key.Key_Down: (0.0, 0.0, -1.0),
}


def nudge_step(key: Qt.Key, modifiers: Qt.KeyboardModifier) -> Translation | None:
    """The move one key press asks for, or None when the key is not a nudge and must keep its usual job."""
    if not modifiers & Qt.KeyboardModifier.AltModifier: return None
    keys = CTRL_AXIS_KEYS if modifiers & Qt.KeyboardModifier.ControlModifier else AXIS_KEYS
    if key not in keys: return None
    step = FINE_STEP_MM if modifiers & Qt.KeyboardModifier.ShiftModifier else STEP_MM
    dx, dy, dz = keys[key]
    return (dx * step, dy * step, dz * step)


def nudged(current: Translation, step: Translation) -> Translation:
    """The move after one nudge, kept to the popup's ±300 mm and 3 decimals."""
    dx, dy, dz = (round(min(max(now + by, -RANGE_MM), RANGE_MM), 3) for now, by in zip(current, step))
    return (dx, dy, dz)


class NudgeKeys(QObject):
    """An event filter that turns nudge keys on the widgets it watches into calls to nudge.

    nudge returns whether it used the step. A key it does not use reaches the widget as before.
    """

    def __init__(self, nudge: Callable[[Translation], bool]):
        super().__init__()
        self.nudge = nudge

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:  # PySide hands a KeyPress over as a QKeyEvent
            step = nudge_step(Qt.Key(event.key()), event.modifiers())
            if step is not None and self.nudge(step): return True
        return super().eventFilter(watched, event)
