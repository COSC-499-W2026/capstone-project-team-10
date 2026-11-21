"""Alt (Option on a Mac) with an arrow or Page key nudges the selected applicator in the plan's X, Y and Z."""
from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QCheckBox, QGridLayout, QPushButton, QWidget

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
    return scaled(keys[key], bool(modifiers & Qt.KeyboardModifier.ShiftModifier))


def scaled(direction: Translation, fine: bool) -> Translation:
    """One nudge along a unit direction, 1 mm or, when fine, 0.1 mm."""
    step = FINE_STEP_MM if fine else STEP_MM
    dx, dy, dz = direction
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


PAD_BUTTONS = (  # key, button text, row, column, the move it makes, the key's name
    (Qt.Key.Key_Up, "↑", 0, 1, "Y +", "↑"),
    (Qt.Key.Key_Left, "←", 1, 0, "X −", "←"),
    (Qt.Key.Key_Down, "↓", 1, 1, "Y −", "↓"),
    (Qt.Key.Key_Right, "→", 1, 2, "X +", "→"),
    (Qt.Key.Key_PageUp, "Z +", 0, 3, "Z +", "Page Up"),
    (Qt.Key.Key_PageDown, "Z −", 1, 3, "Z −", "Page Down"),
)


class NudgePad(QWidget):
    """On-screen buttons for the same nudges as the keys, laid out like the arrow keys, with Z beside them."""

    def __init__(self, nudge: Callable[[Translation], bool]):
        super().__init__()
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        self.buttons: dict[Qt.Key, QPushButton] = {}
        for key, text, row, column, move, name in PAD_BUTTONS:
            button = QPushButton(text)
            button.setToolTip(f"Move {move} by 1 mm, or 0.1 mm with Fine. Alt and {name} do the same, Option on a Mac")
            button.clicked.connect(lambda _checked=False, direction=AXIS_KEYS[key]: nudge(scaled(direction, self.fine.isChecked())))
            grid.addWidget(button, row, column)
            self.buttons[key] = button
        self.fine = QCheckBox("Fine, 0.1 mm steps")
        self.fine.setStyleSheet("QCheckBox { color: rgb(0, 0, 0); } QCheckBox:disabled { color: rgb(150, 150, 150); }")  # the group styles QLabel only, and macOS dark mode drew this white
        grid.addWidget(self.fine, 2, 0, 1, 4)
