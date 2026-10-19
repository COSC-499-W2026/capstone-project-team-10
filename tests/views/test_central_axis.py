"""Central-axis overlay geometry and controls, without a native renderer."""

import pytest


@pytest.fixture
def viewport_module(units_app):
    """Load viewport code after the shared app isolates user files.

    Import failures stop these checks; no native canvas is created by this helper.
    """
    from windows.views import viewport
    return viewport


def test_axis_segment_tracks_cylinder_length(viewport_module):
    """The centre line follows local Z and extends beyond both cylinder ends.

    Wrong axes or a stale length fail these assertions and could mislead alignment review.
    """
    assert viewport_module.central_axis_segment(100) == ((0, 0, -10), (0, 0, 110))
    assert viewport_module.central_axis_segment(200) == ((0, 0, -20), (0, 0, 220))


@pytest.mark.parametrize('length', [None, 0, -10, float('nan'), float('inf')])
def test_unavailable_axis_has_no_geometry(viewport_module, length):
    """Missing or invalid cylinder lengths must not produce an axis.

    Fails if an empty or malformed scene gets a misleading reference line.
    """
    assert viewport_module.central_axis_segment(length) is None


def test_axis_toggle_availability_and_preference(viewport_module):
    """The button is unavailable before a model and preserves the visibility choice.

    Fails if empty scenes permit an axis or a model refresh reverses the user's toggle.
    This exercises the real widget without initializing the native viewport.
    """
    canvas = viewport_module.OrbitCameraViewer3d()
    button = canvas.central_axis_button
    assert not button.isEnabled()
    assert button.isChecked()
    canvas.set_axis_length(100)
    assert button.isEnabled()
    button.click()
    assert not button.isChecked()
    canvas.set_axis_length(150)
    assert not button.isChecked()
    canvas.set_axis_length(None)
    assert not button.isEnabled()
    canvas.close()


def test_scene_reset_notifies_viewport_to_clear(units_app):
    """Reset emits an empty scene so the viewport removes old geometry and its axis.

    Fails if reset only clears the model dictionary, leaving the previous plan visible.
    """
    from PySide6.QtTest import QSignalSpy
    from windows.models.display_model import DisplayModel
    model = DisplayModel()
    emitted = QSignalSpy(model.shapes_changed)
    model.reset()
    assert emitted.count() == 1
    assert emitted.at(0) == [[], False]
