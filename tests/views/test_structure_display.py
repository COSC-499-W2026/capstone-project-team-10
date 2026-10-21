"""Anatomy preview state and its Import controls without a native canvas."""
from pathlib import Path
import pytest
from classes.dicom.data import DicomData
from classes.dicom.structures import Contour, Structure, StructureType


@pytest.fixture
def anatomy_model(units_app):
    """Build an isolated anatomy model with a closed organ and a reference axis.

    Import errors fail this helper; literal coordinates allow bounds checks to catch
    misplaced anatomy without relying on the production transform for expectations.
    """
    from windows.models.structures_model import StructuresModel
    model = StructuresModel()
    plan = DicomData()
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.central_channel_roi = 1
    plan.structures = (
        Structure(1, 'Axis', 'frame', (255, 255, 255), None, StructureType.OTHER, ()),
        Structure(2, 'Organ', 'frame', (0, 255, 0), 'ORGAN', StructureType.ORGAN,
                  (Contour('CLOSED_PLANAR', ((0., 0., 5.), (2., 0., 5.), (0., 2., 5.))),)),
        Structure(3, 'Wrong frame', 'different', (255, 0, 0), 'ORGAN', StructureType.ORGAN,
                  (Contour('CLOSED_PLANAR', ((0., 0., 5.), (2., 0., 5.), (0., 2., 5.))),)),
    )
    model.load_plan(plan, 20.)
    return model


def test_organs_show_by_default_but_unregistered_geometry_is_unavailable(anatomy_model):
    """Show valid organs and refuse anatomy from another patient frame.

    Missing preview or inclusion of ROI 3 fails; mismatched anatomy could otherwise
    imply a false relationship between a needle and an organ.
    """
    assert anatomy_model.visible == {2}
    assert len(anatomy_model.presentations()) == 1
    assert 'frame' in anatomy_model.unavailable[3].lower()
    with pytest.raises(ValueError):
        anatomy_model.set_visible(3, True)


def test_anatomy_length_change_and_hide_preserve_geometry(anatomy_model):
    """Shift the anatomy with the needle tip and allow reversible visibility.

    Wrong Z bounds or lost visibility fails and would misalign the contour preview
    after changing cylinder length.
    """
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib
    from windows.models.structures_model import StructureDisplayMode
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    anatomy_model.set_length(30.)
    bounds = Bnd_Box()
    brepbndlib.AddOptimal(anatomy_model.presentations()[0].outline, bounds)
    assert bounds.Get()[2] == pytest.approx(25., abs=1e-6)
    anatomy_model.set_visible(2, False)
    assert anatomy_model.presentations() == ()
    anatomy_model.set_visible(2, True)
    assert len(anatomy_model.presentations()) == 1
    anatomy_model.clear()
    assert anatomy_model.presentations() == ()
    assert anatomy_model.structures == {}


def test_import_list_checkboxes_control_anatomy_and_failed_import_clears_it(channels_window, tmp_path: Path):
    """Use real Import checkboxes and verify a failed new import clears old anatomy.

    A missing checkbox update or remaining preview after failure fails; the previous
    patient's contours must not survive an import attempt.
    """
    from PySide6.QtCore import Qt
    view = channels_window.navigationmodel.views[0]
    model = channels_window.structuresmodel
    view.action_update_structure_list()
    item = view.structure_list.item(0)
    roi = item.data(Qt.UserRole)
    assert roi == 1
    item.setCheckState(Qt.Checked)
    assert roi in model.visible
    assert model.presentations()
    view.structure_list.item(0).setCheckState(Qt.Unchecked)
    assert roi not in model.visible
    assert all(not label.startswith('structure:') for label in channels_window.displaymodel.shapes)
    view.import_dicom_from_folder(str(tmp_path))
    assert not model.structures
    assert not model.presentations()


def test_single_slice_outlines_are_available_on_request(anatomy_model):
    """Keep an outline available on request when there are too few slices for a surface.

    Losing the ROI or silently presenting an invented volume fails; users must see
    why a surface is unavailable while retaining the actual DICOM outline.
    """
    from windows.models.structures_model import StructureDisplayMode
    anatomy_model.set_mode(StructureDisplayMode.SURFACE)
    presentation = anatomy_model.presentations()[0]
    assert presentation.surface is None
    assert 'two contour slices' in anatomy_model.surface_errors[2]
    assert presentation.outline is None
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    assert not anatomy_model.presentations()[0].outline.IsNull()


def test_surface_follows_probe_length_and_opacity_rejects_invalid_values(anatomy_model):
    """Keep reconstructed vertices aligned through length and visibility changes.

    A stale surface Z coordinate or accepted invalid opacity fails and could hide
    anatomy or leave it at a different position from its contour outlines.
    """
    from dataclasses import replace
    from windows.models.structures_model import StructureDisplayMode
    plan = DicomData()
    plan.central_channel_roi = 1
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    organ = anatomy_model.structures[2]
    plan.structures = (anatomy_model.structures[1], replace(organ, contours=tuple(
        Contour('CLOSED_PLANAR', ((0., 0., z), (4., 0., z), (0., 4., z))) for z in (2., 4., 6.))))
    anatomy_model.load_plan(plan, 20.)
    anatomy_model.set_mode(StructureDisplayMode.BOTH)
    mesh = anatomy_model.presentations()[0].surface
    assert mesh is not None
    before = mesh.Node(1).Z()
    anatomy_model.set_length(30.)
    assert anatomy_model.presentations()[0].surface.Node(1).Z() == pytest.approx(before + 10.)
    anatomy_model.set_opacity(0.6)
    assert anatomy_model.opacity == 0.6
    for invalid in (-0.1, 1.1, float('nan')):
        with pytest.raises(ValueError):
            anatomy_model.set_opacity(invalid)
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    assert anatomy_model.visible == {2}


def test_import_surface_controls_change_shared_display_state(cylinder_window):
    """Drive real mode and opacity widgets without initialising the native canvas.

    Missing connections or stale model values fail; the visible controls must govern
    the same anatomy state used by the viewport.
    """
    from windows.models.structures_model import StructureDisplayMode
    view = cylinder_window.navigationmodel.views[0]
    view.surface_mode.setCurrentText('Both')
    assert cylinder_window.structuresmodel.mode == StructureDisplayMode.BOTH
    view.surface_mode.setCurrentText('Surface')
    view.surface_opacity.setValue(65)
    assert cylinder_window.structuresmodel.mode == StructureDisplayMode.SURFACE
    assert cylinder_window.structuresmodel.opacity == 0.65


def test_surface_presentation_uses_mesh_mode_and_dicom_colour(units_app):
    """Configure the real triangulation actor independently of the shaded-solid mode.

    Missing mesh display mode or shading colour fails; native inspection showed that
    inheriting the solid viewer mode makes an otherwise valid surface invisible.
    """
    from OCC.Core.Poly import Poly_Triangulation, Poly_Triangle
    from OCC.Core.gp import gp_Pnt
    from windows.views.viewport import anatomy_surface_presentation
    mesh = Poly_Triangulation(3, 1, False)
    for index, point in enumerate(((0., 0., 0.), (1., 0., 0.), (0., 1., 0.)), 1):
        mesh.SetNode(index, gp_Pnt(*point))
    mesh.SetTriangle(1, Poly_Triangle(1, 2, 3))
    mesh.ComputeNormals()
    actor = anatomy_surface_presentation(mesh, (0, 255, 0), 0.6)
    assert actor.HasDisplayMode()
    assert actor.DisplayMode() == 0
    colour = actor.Attributes().ShadingAspect().Color()
    assert colour.Green() == pytest.approx(1.)
    assert colour.Red() == pytest.approx(0.)
    assert actor.Transparency() == pytest.approx(0.4)


def test_large_external_body_can_be_selected_as_a_surface(anatomy_model):
    """Reconstruct a large external envelope when selected in Surface mode.

    A 400 by 200 by 400 mm body exceeds the fine-grid budget; a missing surface
    fails and catches the silently invisible BODY reported during import.
    """
    from dataclasses import replace
    plan = DicomData()
    plan.central_channel_roi = 1
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    body = replace(anatomy_model.structures[2], name='BODY', interpreted_type='EXTERNAL',
                   category=StructureType.OTHER, contours=tuple(
                       Contour('CLOSED_PLANAR', ((0., 0., z), (400., 0., z),
                                                (400., 200., z), (0., 200., z)))
                       for z in (0., 400.)))
    plan.structures = (anatomy_model.structures[1], body)
    anatomy_model.load_plan(plan, 20.)
    anatomy_model.set_visible(2, True)
    assert anatomy_model.presentations()[0].surface is not None
    assert not anatomy_model.surface_errors


def test_surface_mode_defers_outlines_and_mode_switch_reuses_them(anatomy_model):
    """Build outlines only when requested, preserving cached geometry on toggles.

    An eagerly built outline or a replaced cached outline fails; this avoids paying
    the CAD wire construction cost when the user only wants surfaces.
    """
    from windows.models.structures_model import StructureDisplayMode
    assert anatomy_model.presentations()[0].outline is None
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    outline = anatomy_model.presentations()[0].outline
    assert outline is not None and not outline.IsNull()
    anatomy_model.set_mode(StructureDisplayMode.SURFACE)
    anatomy_model.set_visible(2, False)
    anatomy_model.set_visible(2, True)
    anatomy_model.set_mode(StructureDisplayMode.BOTH)
    assert anatomy_model.presentations()[0].outline is outline


def test_hidden_anatomy_gets_current_alignment_when_shown(anatomy_model):
    """Regenerate deferred outlines after a hidden structure's probe length changes.

    Old Z bounds fail after hide, length change and show; cached anatomy must not
    reappear in the wrong position relative to the patient's needle paths.
    """
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib
    from windows.models.structures_model import StructureDisplayMode
    anatomy_model.set_visible(2, False)
    anatomy_model.set_length(30.)
    anatomy_model.set_visible(2, True)
    assert anatomy_model.presentations()[0].outline is None
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    bounds = Bnd_Box()
    brepbndlib.AddOptimal(anatomy_model.presentations()[0].outline, bounds)
    assert bounds.Get()[2] == pytest.approx(25., abs=1e-6)
