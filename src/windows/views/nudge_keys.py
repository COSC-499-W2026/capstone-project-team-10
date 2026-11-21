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
    Every nudge rebuilds the needle, so while a used key is held its repeats are added up and
    nudged once, when the key is let go or the widget loses the focus.
    """

    def __init__(self, nudge: Callable[[Translation], bool]):
        super().__init__()
        self.nudge = nudge
        self.held: Translation | None = None  # the repeats added up since the used press, None when no used key is down

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:  # PySide hands a KeyPress over as a QKeyEvent
            step = nudge_step(Qt.Key(event.key()), event.modifiers())
            if step is not None and event.isAutoRepeat() and self.held is not None:
                self.held = (self.held[0] + step[0], self.held[1] + step[1], self.held[2] + step[2])
                return True
            if step is not None and not event.isAutoRepeat() and self.nudge(step):
                self.held = (0.0, 0.0, 0.0)
                return True
        elif event.type() == QEvent.Type.FocusOut or (event.type() == QEvent.Type.KeyRelease and not event.isAutoRepeat()):
            self.release()
        return super().eventFilter(watched, event)

    def release(self) -> None:
        """Nudge by the repeats held back, if any, and stop holding."""
        held, self.held = self.held, None
        if held is not None and held != (0.0, 0.0, 0.0):
            self.nudge(held)
