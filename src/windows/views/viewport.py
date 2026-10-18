from OCC.Core.Graphic3d import Graphic3d_NOM_TRANSPARENT
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Display import OCCViewer

from PySide6 import QtCore, QtGui, QtWidgets

from classes.app import get_app
from classes.logger import log


def wheel_zoom_factor(angle_delta: int, pixel_delta: int) -> float:
    """Return a reversible zoom scale, including pixel-only trackpad events."""
    steps = angle_delta / 120.0 if angle_delta else pixel_delta / 30.0
    return 1.15 ** max(-10.0, min(10.0, steps))


class CameraGesture:
    """Track a single button gesture without touching the native viewer."""

    def __init__(self, button: QtCore.Qt.MouseButton, x: int, y: int, threshold: int):
        self.button = button
        self.origin = (x, y)
        self.previous = (x, y)
        self.threshold = threshold
        self.dragged = False

    def move(self, x: int, y: int) -> tuple[str, int, int]:
        """Distinguish click jitter from a drag and return camera movement."""
        distance = abs(x - self.origin[0]) + abs(y - self.origin[1])
        self.dragged = self.dragged or distance >= self.threshold
        if not self.dragged:
            return ('none', 0, 0)
        dx, dy = x - self.previous[0], self.previous[1] - y
        self.previous = (x, y)
        if self.button == QtCore.Qt.LeftButton:
            return ('rotate', dx, dy)
        if self.button in (QtCore.Qt.RightButton, QtCore.Qt.MiddleButton):
            return ('pan', dx, dy)
        return ('none', 0, 0)

    def select_on_release(self, x: int, y: int) -> bool:
        """Select only a left click that never crossed the drag threshold."""
        self.move(x, y)
        return self.button == QtCore.Qt.LeftButton and not self.dragged


class qtBaseViewer(QtWidgets.QWidget):
    """The base Qt Widget for an OCC viewer"""

    def __init__(self, parent=None):
        super(qtBaseViewer, self).__init__(parent)
        self._display = OCCViewer.Viewer3d()

        # enable Mouse Tracking
        self.setMouseTracking(True)
 
        # Strong focus
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.WheelFocus)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NativeWindow)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_PaintOnScreen)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)

        self.setAutoFillBackground(False)

    def resizeEvent(self, event):
        super(qtBaseViewer, self).resizeEvent(event)
        self._display.View.MustBeResized()

    def paintEngine(self):
        return None


# ref   https://github.com/tpaviot/pythonocc-core/blob/master/src/Display/OCCViewer.py
#       https://github.com/tpaviot/pythonocc-core/blob/master/src/Display/qtDisplay.py
class OrbitCameraViewer3d(qtBaseViewer):
    # emit signal when selection is changed
    # is a list of TopoDS_*
    sig_topods_selected = QtCore.Signal(list)

    def update_display(self, shapes: list, resize: bool = True):
        log.debug(f"updating viewport: {[shape.label for shape in shapes]}")
        # clear all the shapes
        self._display.Context.RemoveAll(True)

        loggedinfo = ""
        for shape in shapes:
            if not shape.shape: continue
            if shape.selected:
                loggedinfo += f"\n    {shape.label}: Type:{shape.type.name} Selected: {shape.selected} rgb: {shape.rgb} Transparent: {shape.transparent}"
            rgb = shape.material["rgb"]
            transparent = shape.material["transparent"]
            colour = Quantity_Color(
                    rgb[0], rgb[1], rgb[2], Quantity_TOC_RGB)
            
            if transparent: self._display.DisplayShape(shape.shape, color=colour, material=Graphic3d_NOM_TRANSPARENT, update=False)
            else: self._display.DisplayShape(shape.shape, color=colour, update=False)

        self._display.Repaint()
        # set the grid model

        # resize
        if resize: self._display.FitAll()
        log.info(loggedinfo)

    def __init__(self, *kargs):
        qtBaseViewer.__init__(self, *kargs)

        self.setObjectName("qt_viewer_3d")

        self._drawbox = False
        self._zoom_area = False
        self._select_area = False
        self._inited = False
        self._leftisdown = False
        self._middleisdown = False
        self._rightisdown = False
        self._selection = None
        self._drawtext = True
        self._qApp = get_app()
        self._current_cursor = "arrow"
        self._available_cursors = {}
        self._gesture: CameraGesture | None = None
        self.setToolTip("Left drag to rotate • Right or middle drag to pan • Scroll to zoom")

    @property
    def qApp(self):
        # reference to QApplication instance
        return self._qApp

    @qApp.setter
    def qApp(self, value):
        self._qApp = value

    def InitDriver(self):
        self._display.Create(window_handle=int(self.winId()), parent=self)
        # background gradient
        self._display.SetModeShaded()
        self._inited = True

    def keyPressEvent(self, event):
        code = event.key()
        if code in self._key_map:
            self._key_map[code]()
        elif code in range(256):
            pass

    def focusInEvent(self, event):
        if self._inited:
            self._display.Repaint()

    def focusOutEvent(self, event):
        if self._inited:
            self._display.Repaint()

    def paintEvent(self, event):
        if not self._inited:
            self.InitDriver()

        self._display.Context.UpdateCurrentViewer()

        if self._drawbox:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            rect = QtCore.QRect(*self._drawbox)
            painter.drawRect(rect)

    def wheelEvent(self, event):
        factor = wheel_zoom_factor(event.angleDelta().y(), event.pixelDelta().y())
        if factor != 1.0:
            self._display.ZoomFactor(factor)
        event.accept()

    @property
    def cursor(self):
        return self._current_cursor

    @cursor.setter
    def cursor(self, value):
        if self._current_cursor != value:
            self._current_cursor = value
            if cursor := self._available_cursors.get(value):
                self.qApp.setOverrideCursor(cursor)
            else:
                self.qApp.restoreOverrideCursor()

    def mousePressEvent(self, event):
        self.setFocus()
        pt = event.position().toPoint()
        if self._gesture is not None:
            self._gesture.dragged = True
            return
        self._gesture = CameraGesture(
            event.button(), pt.x(), pt.y(), QtWidgets.QApplication.startDragDistance()
        )
        self.dragStartPosX, self.dragStartPosY = pt.x(), pt.y()
        if event.button() == QtCore.Qt.LeftButton:
            self._display.StartRotation(pt.x(), pt.y())
        event.accept()

    def mouseReleaseEvent(self, event):
        pt = event.position().toPoint()
        gesture = self._gesture
        if gesture is not None and event.button() == gesture.button:
            self._gesture = None
            if gesture.select_on_release(pt.x(), pt.y()):
                self._display.Select(pt.x(), pt.y())
                if self._display.selected_shapes is not None:
                    self.sig_topods_selected.emit(self._display.selected_shapes)
        self.unsetCursor()
        event.accept()

    def DrawBox(self, event):
        tolerance = 2
        pt = event.pos()
        dx = pt.x() - self.dragStartPosX
        dy = pt.y() - self.dragStartPosY
        if abs(dx) <= tolerance and abs(dy) <= tolerance:
            return
        self._drawbox = [self.dragStartPosX, self.dragStartPosY, dx, dy]

    def mouseMoveEvent(self, event):
        pt = event.position().toPoint()
        self._drawbox = False
        gesture = self._gesture
        if gesture is not None and event.buttons() == gesture.button:
            action, dx, dy = gesture.move(pt.x(), pt.y())
            if action == 'rotate':
                self.setCursor(QtCore.Qt.ClosedHandCursor)
                self._display.Rotation(pt.x(), pt.y())
            elif action == 'pan':
                self.setCursor(QtCore.Qt.SizeAllCursor)
                self._display.Pan(dx, dy)
        elif event.buttons() == QtCore.Qt.NoButton:
            self._gesture = None
            self.unsetCursor()
            self._display.MoveTo(pt.x(), pt.y())
        event.accept()
