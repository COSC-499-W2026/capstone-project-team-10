from dataclasses import dataclass
from math import ceil, floor, isfinite, log10

from OCC.Core.AIS import AIS_InteractiveObject, AIS_Shape, AIS_TextLabel
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.gp import gp_Pnt
from OCC.Core.Prs3d import Prs3d_LineAspect
from OCC.Core.Aspect import Aspect_TOL_DASH
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.Graphic3d import Graphic3d_NOM_TRANSPARENT, Graphic3d_HTA_CENTER
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB, Quantity_TOC_sRGB
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Display import OCCViewer

from PySide6 import QtCore, QtGui, QtWidgets

from classes.app import get_app
from classes.logger import log


# Graphic3d_ZLayerId.hxx defines Topmost as -3; pythonocc does not export this enum.
TOPMOST_Z_LAYER = -3


def central_axis_segment(length: float | None) -> tuple[
    tuple[float, float, float], tuple[float, float, float]
] | None:
    """Cylinder centre line in model millimetres, extended 10% at each end."""
    if length is None or not isfinite(length) or length <= 0:
        return None
    margin = length * 0.1
    return ((0.0, 0.0, -margin), (0.0, 0.0, length + margin))


GridPoint = tuple[float, float, float]
GridBounds = tuple[float, float, float, float, float, float]
GridLine = tuple[GridPoint, GridPoint]


@dataclass(frozen=True)
class GridLabel:
    text: str
    position: GridPoint


@dataclass(frozen=True)
class ReferenceGrid:
    lower: GridPoint
    upper: GridPoint
    lines: tuple[GridLine, ...]
    labels: tuple[GridLabel, ...]


def grid_ticks(lower: float, upper: float) -> tuple[int, ...]:
    """Enclose model bounds with readable 1/2/5-based steps of at least 10 mm."""
    if not isfinite(lower) or not isfinite(upper) or upper < lower:
        raise ValueError('Grid bounds must be finite and ordered')
    target = max(10, (upper - lower) / 10)
    decade = 10 ** floor(log10(target))
    step = next(multiplier * decade for multiplier in (1, 2, 5, 10)
                if multiplier * decade >= target)
    start, stop = floor(lower / step) * step, ceil(upper / step) * step
    if start == stop:
        stop += step
    return tuple(range(start, stop + step, step))


def reference_grid(bounds: GridBounds) -> ReferenceGrid:
    """Build an outer-wall lattice and model-coordinate labels."""
    xs, ys, zs = (grid_ticks(bounds[i], bounds[i + 3]) for i in range(3))
    x0, x1, y0, y1, z0, z1 = xs[0], xs[-1], ys[0], ys[-1], zs[0], zs[-1]
    lines: set[GridLine] = set()
    for x in xs:
        lines.add(((x, y0, z0), (x, y1, z0)))
        lines.add(((x, y1, z0), (x, y1, z1)))
    for y in ys:
        lines.add(((x0, y, z0), (x1, y, z0)))
        lines.add(((x0, y, z0), (x0, y, z1)))
    for z in zs:
        lines.add(((x0, y0, z), (x0, y1, z)))
        lines.add(((x0, y1, z), (x1, y1, z)))
    xm, ym, zm = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    gap = max(x1 - x0, y1 - y0) * 0.12
    labels = [GridLabel(str(x), (x, y0 - gap, z0)) for x in xs]
    labels += [GridLabel(str(y), (x1 + gap, y, z0)) for y in ys]
    labels += [GridLabel(str(z), (x0 - gap, y0, z)) for z in zs]
    labels += [GridLabel('X (mm)', (xm, y0 - 5 * gap, z0)),
               GridLabel('Y (mm)', (x1 + 5 * gap, ym, z0)),
               GridLabel('Z (mm)', (x0 - 5 * gap, y0, zm))]
    return ReferenceGrid((x0, y0, z0), (x1, y1, z1), tuple(sorted(lines)), tuple(labels))


def grid_text_label(annotation: GridLabel) -> AIS_TextLabel:
    """Create screen-readable native text at a model-coordinate anchor."""
    label = AIS_TextLabel()
    label.SetText(annotation.text)
    label.SetFont("Arial")
    label.SetHJustification(Graphic3d_HTA_CENTER)
    label.SetPosition(gp_Pnt(*annotation.position))
    label.SetColor(Quantity_Color(0.92, 0.94, 0.96, Quantity_TOC_RGB))
    label.SetHeight(16 if 'mm' in annotation.text else 12)
    label.SetZoomable(False)
    return label


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
        self._grid_presentations.clear()
        self._axis_presentation = None
        bounds = Bnd_Box()

        loggedinfo = ""
        for shape in shapes:
            if not shape.shape or shape.shape.IsNull(): continue
            brepbndlib.AddOptimal(shape.shape, bounds)
            if shape.selected:
                loggedinfo += f"\n    {shape.label}: Type:{shape.type.name} Selected: {shape.selected} rgb: {shape.rgb} Transparent: {shape.transparent}"
            rgb = shape.material["rgb"]
            transparent = shape.material["transparent"]
            colour = Quantity_Color(
                    rgb[0], rgb[1], rgb[2], Quantity_TOC_RGB)
            
            if transparent: self._display.DisplayShape(shape.shape, color=colour, material=Graphic3d_NOM_TRANSPARENT, update=False)
            else: self._display.DisplayShape(shape.shape, color=colour, update=False)

        self._grid_definition = None if bounds.IsVoid() else reference_grid(bounds.Get())
        self.set_grid_available(self._grid_definition is not None)
        if resize:
            self._display.View.ZFitAll()
            self._display.View.FitAll(0.2, False)
        self._display.Repaint()
        cylinder = get_app().window.cylindermodel.cylinder
        self.set_axis_length(cylinder.length if shapes and cylinder is not None else None)
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
        self._grid_available = False
        self._grid_definition: ReferenceGrid | None = None
        self._grid_presentations: list[AIS_InteractiveObject] = []
        self.grid_button = QtWidgets.QToolButton(self)
        self.grid_button.setText("XYZ grid (mm)")
        self.grid_button.setToolTip("Outer bounding-box grid; model XYZ coordinates in millimetres")
        self.grid_button.setCheckable(True)
        self.grid_button.setChecked(True)
        self.grid_button.setEnabled(False)
        self.grid_button.setStyleSheet(
            "QToolButton { background: #30343b; color: white; padding: 7px 12px;"
            " border: 1px solid #727982; border-radius: 5px; }"
            "QToolButton:checked { background: #244e69; border-color: #7bc5ef; }"
            "QToolButton:disabled { color: #999999; background: #3d3d3d; }"
        )
        self.grid_button.toggled.connect(self._refresh_grid)
        self.grid_button.adjustSize()
        self._position_grid_button()
        self._axis_length: float | None = None
        self._axis_presentation: AIS_Shape | None = None
        self.central_axis_button = QtWidgets.QToolButton(self)
        self.central_axis_button.setObjectName("central_axis_toggle")
        self.central_axis_button.setText("Central axis")
        self.central_axis_button.setToolTip("Show the cylinder centre line as a reference overlay")
        self.central_axis_button.setCheckable(True)
        self.central_axis_button.setChecked(True)
        self.central_axis_button.setEnabled(False)
        self.central_axis_button.setStyleSheet(
            "QToolButton { background-color: #30343b; color: white; padding: 7px 12px;"
            " border: 1px solid #727982; border-radius: 5px; }"
            "QToolButton:checked { background-color: #665017; color: #ffe297;"
            " border-color: #e2b64e; }"
            "QToolButton:disabled { color: #9a9a9a; background-color: #3d3d3d;"
            " border-color: #555555; }"
        )
        self.central_axis_button.toggled.connect(self._refresh_central_axis)
        self.central_axis_button.adjustSize()
        self._position_axis_button()
        self.setToolTip("Left drag to rotate • Right or middle drag to pan • Scroll to zoom")

    def _position_axis_button(self):
        """Keep the overlay control inset from the viewport's top-right corner."""
        self.central_axis_button.move(
            max(8, self.width() - self.central_axis_button.width() - 12),
            self.grid_button.y() + self.grid_button.height() + 8
        )
        self.central_axis_button.raise_()

    def _position_grid_button(self):
        self.grid_button.move(max(8, self.width() - self.grid_button.width() - 12), 12)
        self.grid_button.raise_()

    def resizeEvent(self, event):
        if self._inited:
            super().resizeEvent(event)
        self._position_grid_button()
        self._position_axis_button()

    def set_grid_available(self, available: bool):
        """Hide the grid in empty scenes without losing the user's toggle choice."""
        self._grid_available = available
        self.grid_button.setEnabled(available)
        self._refresh_grid()

    def _refresh_grid(self):
        """Draw subdued outer-wall lines and white millimetre labels."""
        if not self._inited:
            return
        for presentation in self._grid_presentations:
            self._display.Context.Remove(presentation, False)
        self._grid_presentations.clear()
        grid = self._grid_definition
        if self._grid_available and self.grid_button.isChecked() and grid is not None:
            builder = BRep_Builder()
            lattice = TopoDS_Compound()
            builder.MakeCompound(lattice)
            for start, end in grid.lines:
                builder.Add(lattice, BRepBuilderAPI_MakeEdge(gp_Pnt(*start), gp_Pnt(*end)).Edge())
            wire = AIS_Shape(lattice)
            wire.SetColor(Quantity_Color(0.16, 0.19, 0.23, Quantity_TOC_sRGB))
            wire.SetWidth(1)
            self._show_grid_presentation(wire)
            for annotation in grid.labels:
                self._show_grid_presentation(grid_text_label(annotation))
        self._display.Repaint()

    def _show_grid_presentation(self, presentation: AIS_InteractiveObject):
        self._display.Context.Display(presentation, False)
        self._display.Context.Deactivate(presentation)
        self._grid_presentations.append(presentation)

    def set_axis_length(self, length: float | None):
        """Refresh the reference after a scene change without reframing the camera."""
        self._axis_length = length if central_axis_segment(length) is not None else None
        self.central_axis_button.setEnabled(self._axis_length is not None)
        self._refresh_central_axis()

    def _refresh_central_axis(self):
        """Draw a non-selectable reference on top of solids, outside export geometry."""
        if not self._inited:
            return
        context = self._display.Context
        if self._axis_presentation is not None:
            context.Remove(self._axis_presentation, False)
            self._axis_presentation = None
        segment = central_axis_segment(self._axis_length)
        if self.central_axis_button.isChecked() and segment is not None:
            start, end = segment
            edge = BRepBuilderAPI_MakeEdge(gp_Pnt(*start), gp_Pnt(*end)).Edge()
            axis = AIS_Shape(edge)
            color = Quantity_Color(1.0, 0.78, 0.25, Quantity_TOC_RGB)
            axis.SetColor(color)
            axis.Attributes().SetLineAspect(Prs3d_LineAspect(color, Aspect_TOL_DASH, 2.0))
            axis.SetZLayer(TOPMOST_Z_LAYER)
            context.Display(axis, False)
            context.Deactivate(axis)
            self._axis_presentation = axis
        self._display.Repaint()

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
        background = Quantity_Color(12 / 255, 17 / 255, 23 / 255, Quantity_TOC_sRGB)
        self._display.View.SetBgGradientColors(background, background)
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
