"""Camera gesture rules without a native OpenCASCADE viewport."""

import pytest


@pytest.fixture
def controls(units_app):
    """Import controls with user files isolated before logger initialization.

    This helper fails on import errors and keeps the checks independent of saved settings.
    """
    from windows.views import viewport
    return viewport


def test_left_drag_rotates_without_selecting_on_release(controls):
    """A left drag rotates and remains a drag even after returning to its origin.

    Fails if returning to the press point makes release select a needle accidentally.
    """
    gesture = controls.CameraGesture(controls.QtCore.Qt.LeftButton, 10, 10, 5)
    assert gesture.move(30, 10) == ('rotate', 20, 0)
    gesture.move(10, 10)
    assert not gesture.select_on_release(10, 10)


def test_small_left_motion_is_a_click(controls):
    """Small pointer jitter must not rotate the view or prevent selection.

    Fails if a tiny hand movement rotates instead of selecting the intended needle.
    """
    gesture = controls.CameraGesture(controls.QtCore.Qt.LeftButton, 10, 10, 5)
    assert gesture.move(12, 11) == ('none', 0, 0)
    assert gesture.select_on_release(12, 11)


def test_release_distance_alone_prevents_selection(controls):
    """A distant release is a drag even if Qt delivered no intermediate move.

    Fails if coalesced mouse events cause an unintended needle selection.
    """
    gesture = controls.CameraGesture(controls.QtCore.Qt.LeftButton, 10, 10, 5)
    assert not gesture.select_on_release(40, 10)


@pytest.mark.parametrize('button', ['RightButton', 'MiddleButton'])
def test_pan_uses_incremental_distance_and_never_selects(controls, button):
    """Right and middle drags pan incrementally with the screen Y axis inverted.

    Fails if panning accelerates by reusing the initial origin or selects a needle.
    """
    buttons = {'RightButton': controls.QtCore.Qt.RightButton,
               'MiddleButton': controls.QtCore.Qt.MiddleButton}
    gesture = controls.CameraGesture(buttons[button], 10, 10, 5)
    assert gesture.move(20, 25) == ('pan', 10, -15)
    assert gesture.move(23, 27) == ('pan', 3, -2)
    assert not gesture.select_on_release(23, 27)


def test_zoom_is_smooth_reversible_and_ignores_zero(controls):
    """Wheel distance scales zoom smoothly and opposite movements cancel.

    Fails on the old twofold jump or when a zero-delta event zooms out.
    """
    assert controls.wheel_zoom_factor(0, 0) == 1
    assert controls.wheel_zoom_factor(120, 0) == pytest.approx(1.15)
    assert controls.wheel_zoom_factor(-120, 0) == pytest.approx(1 / 1.15)
    assert 1 < controls.wheel_zoom_factor(30, 0) < 1.15
    assert controls.wheel_zoom_factor(0, 30) == pytest.approx(1.15)


@pytest.mark.parametrize('angle,pixel,expected', [
    ((0, 0), (30, 2), (0.17453292519943295, 1.0)),
    ((0, 0), (-30, 2), (-0.17453292519943295, 1.0)),
    ((120, 0), (0, 0), (0.17453292519943295, 1.0)),
    ((0, 120), (2, 30), (0, 1.15)),
    ((0, 0), (0, 0), (0, 1.0)),
    ((0, 0), (3, 2), (0., 1.)),
    ((0, 0), (2, 3), (0., 1.)),
    ((0, 0), (2, 1), (0., 1.)),
    ((0, 0), (3000, 0), (1.7453292519943295, 1.)),
    ((0, 0), (-3000, 0), (-1.7453292519943295, 1.)),
    ((0, 120), (1, 0), (0., 1.15)),
    ((120, 0), (0, 30), (0.17453292519943295, 1.)),
])
def test_scroll_routes_dominant_axis_without_combining_actions(controls, angle, pixel, expected):
    """Horizontal scrolling produces reversible camera roll in radians; vertical scrolling zooms.

    Wrong units, ambiguous diagonal movement, unbounded roll or inconsistent delta
    precedence fails, preventing jitter from unexpectedly turning the view.
    """
    assert controls.wheel_camera_motion(*angle, *pixel) == pytest.approx(expected)


class RecordingCameraDisplay:
    """Record native display boundary calls without initializing a native canvas."""

    def __init__(self):
        """Initialize a nonzero twist and empty call counters for the handler tests."""
        self.View = self
        self.twist = 0.3
        self.repaints = 0
        self.zoom_factors = []

    def Twist(self):
        """Return the retained twist so successive events can accumulate."""
        return self.twist

    def SetTwist(self, rotation: float):
        """Record the requested orientation; this helper does not emulate geometry."""
        self.twist = rotation

    def Repaint(self):
        """Count explicit redraws so a forgotten repaint fails the handler test."""
        self.repaints += 1

    def ZoomFactor(self, factor: float):
        """Record zoom requests to detect roll accidentally taking the zoom path."""
        self.zoom_factors.append(factor)


@pytest.mark.parametrize('inverted', [False, True])
def test_wheel_handler_accumulates_roll_repaints_and_preserves_zoom(controls, inverted):
    """Drive real Qt wheel events through the real widget and its display boundary.

    Absolute SetTwist, a missing repaint, zoom during roll or double inversion fails.
    Qt already supplies signed deltas; the handler must preserve those directions.
    """
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QWheelEvent
    viewer = controls.OrbitCameraViewer3d()
    display = RecordingCameraDisplay()
    viewer._display = display
    for dx, dy in ((30, 0), (30, 0), (-30, 0)):
        event = QWheelEvent(QPointF(), QPointF(), QPoint(dx, dy), QPoint(),
                            Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, inverted)
        event.ignore()
        viewer.wheelEvent(event)
        assert event.isAccepted()
    assert display.twist == pytest.approx(0.47453292519943295)
    assert display.repaints == 3
    assert display.zoom_factors == []
    for dx, dy in ((0, 30), (0, 0), (3, 2)):
        event = QWheelEvent(QPointF(), QPointF(), QPoint(dx, dy), QPoint(),
                            Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, inverted)
        viewer.wheelEvent(event)
    assert display.twist == pytest.approx(0.47453292519943295)
    assert display.repaints == 3
    assert display.zoom_factors == pytest.approx([1.15])
    viewer.close()
