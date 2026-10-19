"""Bounding-box grid configuration and real Qt control state."""

import pytest


@pytest.fixture
def viewport_module(units_app):
    """Import the viewport after filesystem isolation.

    Import failures stop this helper; isolation prevents loading real user settings.
    """
    from windows.views import viewport
    return viewport


def test_grid_control_tracks_scene_and_preserves_user_choice(viewport_module):
    """Enable the grid for a scene while retaining the user's hidden preference.

    Incorrect enabled or checked state fails and would show a misleading empty
    reference or unexpectedly turn the grid back on after a redraw.
    """
    canvas = viewport_module.OrbitCameraViewer3d()
    button = canvas.grid_button
    assert "mm" in button.text()
    assert not button.isEnabled()
    assert button.isChecked()
    canvas.set_grid_available(True)
    assert button.isEnabled()
    button.click()
    canvas.set_grid_available(False)
    assert not button.isEnabled()
    canvas.set_grid_available(True)
    assert not button.isChecked()
    canvas.resize(800, 500)
    canvas._position_grid_button()
    assert button.x() + button.width() == 788
    canvas.close()


def test_reset_notifies_viewport_of_empty_scene(units_app):
    """Reset must notify the viewport so it can remove the previous model's grid.

    A missing empty-scene signal fails and would leave stale spatial context visible.
    """
    from PySide6.QtTest import QSignalSpy
    from windows.models.display_model import DisplayModel
    model = DisplayModel()
    changes = QSignalSpy(model.shapes_changed)
    model.reset()
    assert changes.count() == 1
    assert changes.at(0) == [[], False]


def test_grid_ticks_are_rounded_and_enclose_geometry(viewport_module):
    """Round bounds outward to readable millimetre ticks, including negative values.

    Missing outer bounds or irregular steps fail and prevent labels that misstate
    the extent of the visible model. Large scenes must not create thousands of labels.
    """
    assert viewport_module.grid_ticks(-26.96, 26.44) == (-30, -20, -10, 0, 10, 20, 30)
    assert viewport_module.grid_ticks(-1, 171.974) == (-20, 0, 20, 40, 60, 80, 100, 120, 140, 160, 180)
    assert viewport_module.grid_ticks(5, 5) == (0, 10)
    assert len(viewport_module.grid_ticks(-10000, 10000)) <= 12


@pytest.mark.parametrize('lower,upper', [(float('nan'), 1), (0, float('inf')), (2, 1)])
def test_grid_rejects_invalid_bounds(viewport_module, lower, upper):
    """Refuse invalid bounds before they become OpenCASCADE geometry.

    A missing ValueError fails and prevents native rendering of nonfinite coordinates.
    """
    with pytest.raises(ValueError):
        viewport_module.grid_ticks(lower, upper)


def test_reference_grid_keeps_lines_on_outer_walls(viewport_module):
    """Place the lattice on three outer walls and label axes in model millimetres.

    Interior lines or patient-direction labels fail, avoiding clutter through the
    model and unsupported anatomical claims after the DICOM coordinate transform.
    """
    grid = viewport_module.reference_grid((-15, -15, 0, 15, 15, 100))
    assert grid.lower == (-20, -20, 0)
    assert grid.upper == (20, 20, 100)
    assert all((a[0] == b[0] == -20) or (a[1] == b[1] == 20)
               or (a[2] == b[2] == 0) for a, b in grid.lines)
    assert len(grid.lines) == len(set(grid.lines))
    assert {label.text for label in grid.labels if 'mm' in label.text} == {'X (mm)', 'Y (mm)', 'Z (mm)'}


def test_grid_label_preserves_text_and_position(viewport_module):
    """Create a real native label from the grid's text and model position.

    Missing or altered text/coordinates fails the assertions. Passing a wrapped
    C++ string rather than Python text crashes this binding, so exercise the seam.
    """
    annotation = viewport_module.GridLabel('X (mm)', (10, -20, 30))
    label = viewport_module.grid_text_label(annotation)
    assert label.Text() == 'X (mm)'
    assert label.Position().Coord() == (10, -20, 30)


def test_grid_and_central_axis_controls_do_not_overlap(viewport_module):
    """Keep both overlay toggles independently clickable after merging the axis feature.

    Overlapping button rectangles fail and would hide one of the controls from the user.
    """
    canvas = viewport_module.OrbitCameraViewer3d()
    canvas.resize(480, 472)
    canvas._position_grid_button()
    canvas._position_axis_button()
    assert not canvas.grid_button.geometry().intersects(canvas.central_axis_button.geometry())
    canvas.set_grid_available(True)
    canvas.set_axis_length(160)
    canvas.grid_button.click()
    assert canvas.central_axis_button.isChecked()
    canvas.central_axis_button.click()
    assert not canvas.grid_button.isChecked()
    canvas.close()
