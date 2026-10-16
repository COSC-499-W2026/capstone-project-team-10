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
