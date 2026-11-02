"""Anatomy preview state and its Import controls without a native canvas."""
from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
import pytest
from classes.dicom.data import DicomData
from classes.dicom.structures import Contour, Structure, StructureType


if TYPE_CHECKING:
    from windows.models.structures_model import StructuresModel


def wait_for_surfaces(model: StructuresModel):
    """Helper that delivers worker results through the real Qt event loop.

    A stalled task fails after ten seconds; consuming queued results prevents tests
    from mistaking scheduled work for a completed, visible organ.
    """
    from time import sleep
    from PySide6.QtCore import QElapsedTimer
    from PySide6.QtTest import QTest
    timer = QElapsedTimer()
    timer.start()
    while model.pending and timer.elapsed() < 10000:
        QTest.qWait(5)
        sleep(0.001)
    assert not model.pending, 'Surface reconstruction did not complete'


@pytest.fixture
def anatomy_model(units_app):
    """Build an isolated anatomy model with a closed organ and a reference axis.

    Import errors fail this helper; literal coordinates allow bounds checks to catch
    misplaced anatomy without relying on the production transform for expectations.
    """
    from windows.models.structures_model import StructuresModel, StructureDisplayMode
    model = StructuresModel()
    model.set_mode(StructureDisplayMode.SURFACE)
    plan = DicomData()
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.central_channel_roi = 1
    plan.probe_frame_uid = '1.2.3'
    plan.structures = (
        Structure(1, 'Axis', '1.2.3', (255, 255, 255), None, StructureType.OTHER, ()),
        Structure(2, 'Organ', '1.2.3', (0, 255, 0), 'ORGAN', StructureType.ORGAN,
                  (Contour('CLOSED_PLANAR', ((0., 0., 5.), (2., 0., 5.), (0., 2., 5.))),)),
        Structure(3, 'Wrong frame', '1.2.4', (255, 0, 0), 'ORGAN', StructureType.ORGAN,
                  (Contour('CLOSED_PLANAR', ((0., 0., 5.), (2., 0., 5.), (0., 2., 5.))),)),
    )
    model.load_plan(plan, 20.)
    wait_for_surfaces(model)
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
    wait_for_surfaces(anatomy_model)
    bounds = Bnd_Box()
    brepbndlib.AddOptimal(anatomy_model.presentations()[0].outline, bounds)
    assert bounds.Get()[2] == pytest.approx(25., abs=1e-6)
    anatomy_model.set_visible(2, False)
    wait_for_surfaces(anatomy_model)
    assert anatomy_model.presentations() == ()
    anatomy_model.set_visible(2, True)
    wait_for_surfaces(anatomy_model)
    assert len(anatomy_model.presentations()) == 1
    anatomy_model.clear()
    assert anatomy_model.presentations() == ()
    assert anatomy_model.structures == {}


def test_structures_tab_lists_only_organs_and_tumours(cylinder_window, anatomy_model):
    """Show organs and tumours on the Structures tab, not applicator needles.

    Fails if Axis (OTHER) appears, or if Organ is missing. Needle-type ROIs
    already live on Channels; listing them here hides the anatomy (FR-SV-01).
    """
    from PySide6.QtCore import Qt
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.structures = tuple(anatomy_model.structures.values())
    cylinder_window.structuresmodel.load_plan(plan, 20.)
    view = cylinder_window.navigationmodel.views[5]
    rois = [
        view.structure_list.item(index).data(Qt.UserRole)
        for index in range(view.structure_list.count())
    ]
    labels = [
        view.structure_list.item(index).text()
        for index in range(view.structure_list.count())
    ]
    assert rois == [2, 3]
    assert all("organ" in label for label in labels)
    assert not any("Axis" in label for label in labels)


def test_structures_tab_shows_body_on_ex1_and_hides_needles(channels_window):
    """Show BODY on Ex1 Structures, and keep Applicator rows on Import only.

    Fails if BODY is missing, if an Applicator row appears on Structures, or if
    Import loses its 42 inventory rows. BODY is the external outline on this
    sample; hiding it with the needles leaves no anatomy on the tab.
    """
    from PySide6.QtCore import Qt
    structures_view = channels_window.navigationmodel.views[5]
    import_view = channels_window.navigationmodel.views[0]
    assert structures_view.structure_list.count() == 1
    assert "BODY" in structures_view.structure_list.item(0).text()
    assert "Applicator" not in structures_view.structure_list.item(0).text()
    assert import_view.structure_list.count() == 42
    import_labels = [
        import_view.structure_list.item(index).text()
        for index in range(import_view.structure_list.count())
    ]
    assert any("Applicator" in label for label in import_labels)
    assert not import_view.structure_list.item(0).flags() & Qt.ItemIsUserCheckable


def test_structures_checkboxes_control_anatomy_and_failed_import_clears_it(channels_window, tmp_path: Path):
    """Verify a failed new import clears anatomy after Ex1, which has no listed organs.

    Remaining preview after failure fails; the previous patient's contours
    must not survive an import attempt.
    """
    model = channels_window.structuresmodel
    channels_window.navigationmodel.views[0].import_dicom_from_folder(str(tmp_path))
    assert not model.structures
    assert not model.presentations()


@pytest.mark.parametrize('probe_frame', ['1.2.3', '1.2.4', None])
def test_nucletron_uses_embedded_probe_frame_not_colliding_rs_roi(anatomy_model, probe_frame):
    """Compare anatomy against the actual private RTPLAN probe coordinate frame.

    A colliding external ROI number must not authorize a mismatched or missing
    embedded frame; otherwise anatomy can appear falsely aligned to the needle.
    """
    from pydicom.dataset import Dataset
    from classes.dicom.fileio import load_central_axis_nucletron
    plan = DicomData()
    plan.central_channel_roi = 1
    plan.structures = tuple(anatomy_model.structures.values())
    definition = Dataset()
    definition.ROINumber = 1
    if probe_frame is not None:
        definition.ReferencedFrameOfReferenceUID = probe_frame
    contour = Dataset()
    contour.ContourData = [0., 0., 10., 0., 0., 0.]
    geometry = Dataset()
    geometry.ReferencedROINumber = 1
    geometry.ContourSequence = [contour]
    embedded = Dataset()
    embedded.StructureSetROISequence = [definition]
    embedded.ROIContourSequence = [geometry]
    load_central_axis_nucletron(plan, [embedded])
    anatomy_model.load_plan(plan, 20.)
    wait_for_surfaces(anatomy_model)
    assert (2 in anatomy_model.visible) == (probe_frame == '1.2.3')
    if probe_frame != '1.2.3':
        assert 2 in anatomy_model.unavailable


def test_empty_display_refresh_preserves_anatomy_until_explicit_reset(cylinder_window, anatomy_model):
    """Separate a transient empty printable scene from clearing the imported plan.

    Losing the organ on an empty refresh, or keeping it after reset, fails; a
    display update must neither erase anatomy nor retain the previous patient.
    """
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.central_channel_roi = 1
    plan.structures = tuple(anatomy_model.structures.values())
    model = cylinder_window.structuresmodel
    model.load_plan(plan, 20.)
    wait_for_surfaces(model)
    cylinder_window.displaymodel.show_shapes([])
    assert model.visible == {2}
    cylinder_window.displaymodel.reset()
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
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    organ = anatomy_model.structures[2]
    plan.structures = (anatomy_model.structures[1], replace(organ, contours=tuple(
        Contour('CLOSED_PLANAR', ((0., 0., z), (4., 0., z), (0., 4., z))) for z in (2., 4., 6.))))
    anatomy_model.load_plan(plan, 20.)
    wait_for_surfaces(anatomy_model)
    anatomy_model.set_mode(StructureDisplayMode.BOTH)
    mesh = anatomy_model.presentations()[0].surface
    assert mesh is not None
    before = mesh.Node(1).Z()
    anatomy_model.set_length(30.)
    wait_for_surfaces(anatomy_model)
    assert anatomy_model.presentations()[0].surface.Node(1).Z() == pytest.approx(before + 10.)
    anatomy_model.set_opacity(2, 0.6)
    assert anatomy_model.opacity_for(2) == 0.6
    for invalid in (-0.1, 1.1, float('nan')):
        with pytest.raises(ValueError):
            anatomy_model.set_opacity(2, invalid)
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    assert anatomy_model.visible == {2}


def test_structures_surface_controls_change_selected_organ_opacity(cylinder_window, anatomy_model):
    """Drive real mode and opacity widgets without initialising the native canvas.

    Missing connections or stale model values fail; the visible controls must govern
    the same anatomy state used by the viewport.
    """
    from windows.models.structures_model import StructureDisplayMode
    view = cylinder_window.navigationmodel.views[5]
    model = cylinder_window.structuresmodel
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.structures = tuple(anatomy_model.structures.values())
    model.load_plan(plan, 20.)
    wait_for_surfaces(model)
    view.structure_list.setCurrentRow(0)
    view.surface_mode.setCurrentText('Both')
    assert cylinder_window.structuresmodel.mode == StructureDisplayMode.BOTH
    view.surface_mode.setCurrentText('Surface')
    view.surface_opacity.setValue(65)
    assert cylinder_window.structuresmodel.mode == StructureDisplayMode.SURFACE
    assert cylinder_window.structuresmodel.opacity_for(2) == 0.65


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
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    body = replace(anatomy_model.structures[2], name='BODY', interpreted_type='EXTERNAL',
                   category=StructureType.OTHER, contours=tuple(
                       Contour('CLOSED_PLANAR', ((0., 0., z), (400., 0., z),
                                                (400., 200., z), (0., 200., z)))
                       for z in (0., 400.)))
    plan.structures = (anatomy_model.structures[1], body)
    anatomy_model.load_plan(plan, 20.)
    wait_for_surfaces(anatomy_model)
    anatomy_model.set_visible(2, True)
    wait_for_surfaces(anatomy_model)
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
    wait_for_surfaces(anatomy_model)
    anatomy_model.set_visible(2, True)
    wait_for_surfaces(anatomy_model)
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
    wait_for_surfaces(anatomy_model)
    anatomy_model.set_length(30.)
    wait_for_surfaces(anatomy_model)
    anatomy_model.set_visible(2, True)
    wait_for_surfaces(anatomy_model)
    assert anatomy_model.presentations()[0].outline is None
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    bounds = Bnd_Box()
    brepbndlib.AddOptimal(anatomy_model.presentations()[0].outline, bounds)
    assert bounds.Get()[2] == pytest.approx(25., abs=1e-6)


def test_opacity_does_not_rebuild_geometry_or_change_other_organs(anatomy_model):
    """Change only the selected ROI's opacity without a structural refresh.

    A geometry-change signal or changing another ROI's alpha fails; slider movement
    must not rebuild BODY meshes or silently change a neighbouring organ.
    """
    from PySide6.QtTest import QSignalSpy
    geometry_changes = QSignalSpy(anatomy_model.changed)
    anatomy_model.set_opacity(2, 0.7)
    assert anatomy_model.opacity_for(2) == 0.7
    assert anatomy_model.opacity_for(1) == 0.45
    assert geometry_changes.count() == 0


def test_failed_surface_is_explained_in_visible_structure_row(cylinder_window, anatomy_model):
    """Expose a failed surface directly in the list while keeping Surface-only mode.

    A checked invisible ROI or a reason confined to a tooltip fails; users must not
    mistake failed reconstruction for absent anatomy.
    """
    from PySide6.QtCore import Qt
    model = cylinder_window.structuresmodel
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.structures = tuple(anatomy_model.structures.values())
    model.load_plan(plan, 20.)
    wait_for_surfaces(model)
    view = cylinder_window.navigationmodel.views[5]
    item = view.structure_list.item(0)
    assert 'Surface unavailable.' in item.text()
    assert 'two contour slices' in item.text()
    assert item.checkState() == Qt.Unchecked
    assert model.presentations()[0].outline is None


def test_outline_failure_does_not_disable_a_valid_surface(anatomy_model):
    """Keep a surface usable when a redundant degenerate loop cannot form a wire.

    Permanent ROI disablement fails after Outlines then Surface; an error in one
    presentation mode must not make the other representation inaccessible.
    """
    from dataclasses import replace
    from windows.models.structures_model import StructureDisplayMode
    organ = anatomy_model.structures[2]
    contours = tuple(Contour('CLOSED_PLANAR', ((0., 0., z), (4., 0., z), (0., 4., z)))
                     for z in (2., 4., 6.))
    degenerate = Contour('CLOSED_PLANAR', ((0., 0., 2.),) * 3)
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.structures = (replace(organ, contours=contours + (degenerate,)),)
    anatomy_model.load_plan(plan, 20.)
    wait_for_surfaces(anatomy_model)
    anatomy_model.set_mode(StructureDisplayMode.OUTLINES)
    anatomy_model.set_mode(StructureDisplayMode.SURFACE)
    anatomy_model.set_visible(2, True)
    wait_for_surfaces(anatomy_model)
    assert anatomy_model.presentations()[0].surface is not None
    assert 2 not in anatomy_model.unavailable


def test_surface_work_returns_to_the_event_loop_and_reset_discards_its_result(anatomy_model, units_app):
    """Leave reconstruction pending and reject late work after clearing the plan.

    Synchronous construction or a stale worker restoring anatomy fails; the UI
    must stay usable and never redisplay a previous patient's organ.
    """
    from dataclasses import replace
    organ = anatomy_model.structures[2]
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.structures = (replace(organ, contours=tuple(
        Contour('CLOSED_PLANAR', ((0., 0., z), (40., 0., z), (0., 40., z)))
        for z in (2., 4., 6.))),)
    anatomy_model.load_plan(plan, 20.)
    assert 'Building' in anatomy_model.status_message(2)
    anatomy_model.clear()
    assert anatomy_model.surface_pool.waitForDone(10000)
    units_app.processEvents()
    assert not anatomy_model.structures
    assert not anatomy_model.presentations()
    assert not anatomy_model.surface_errors


def test_late_surface_cannot_supply_a_new_plan_with_the_same_roi(anatomy_model, units_app):
    """Reject an old plan's completed mesh before showing a reused ROI number.

    A 40 mm mesh in the new 4 mm organ fails; import/reset must invalidate queued
    results, even when both plans use the same ROI number and reference frame.
    """
    from dataclasses import replace
    organ = anatomy_model.structures[2]
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.structures = (replace(organ, contours=tuple(
        Contour('CLOSED_PLANAR', ((0., 0., z), (40., 0., z), (0., 40., z)))
        for z in (2., 4., 6.))),)
    anatomy_model.load_plan(plan, 20.)
    assert anatomy_model.surface_pool.waitForDone(10000)
    plan.structures = (replace(organ, category=StructureType.OTHER, contours=tuple(
        Contour('CLOSED_PLANAR', ((0., 0., z), (4., 0., z), (0., 4., z)))
        for z in (2., 4., 6.))),)
    anatomy_model.load_plan(plan, 20.)
    units_app.processEvents()
    anatomy_model.set_visible(2, True)
    wait_for_surfaces(anatomy_model)
    mesh = anatomy_model.presentations()[0].surface
    assert max(mesh.Node(i).X() for i in range(1, mesh.NbNodes() + 1)) == pytest.approx(4.5)


def test_pending_surface_uses_latest_probe_length(anatomy_model):
    """Realign a completed background mesh when the probe length changes mid-job.

    A stale maximum Z fails after changing length before event delivery; anatomy
    must move with the needles even when reconstruction started earlier.
    """
    from dataclasses import replace
    organ = anatomy_model.structures[2]
    plan = DicomData()
    plan.probe_frame_uid = '1.2.3'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.structures = (replace(organ, contours=tuple(
        Contour('CLOSED_PLANAR', ((0., 0., z), (4., 0., z), (0., 4., z)))
        for z in (2., 4., 6.))),)
    anatomy_model.load_plan(plan, 20.)
    anatomy_model.set_length(30.)
    wait_for_surfaces(anatomy_model)
    mesh = anatomy_model.presentations()[0].surface
    assert max(mesh.Node(i).Z() for i in range(1, mesh.NbNodes() + 1)) == pytest.approx(26.5)


@pytest.mark.parametrize('failure', [IndexError, TypeError, MemoryError])
def test_unexpected_surface_failure_still_emits_a_result(anatomy_model, failure):
    """Report unexpected library failures instead of leaving reconstruction pending.

    A raised exception or absent error result fails; the UI must stop showing
    Building when the worker has already stopped.
    """
    from PySide6.QtTest import QSignalSpy
    from windows.models.structures_model import SurfaceTask
    class FailingSurfaceTask(SurfaceTask):
        def reconstruct(self):
            """Helper raising a library failure to exercise the worker's error boundary."""
            raise failure('library failure')
    task = FailingSurfaceTask(anatomy_model._generation, anatomy_model.structures[2], anatomy_model.alignment, None)
    finished = QSignalSpy(task.signals.finished)
    anatomy_model.pending.add(2)
    task.signals.finished.connect(anatomy_model._accept_surface)
    task.run()
    assert finished.count() == 1
    assert finished.at(0)[0].error == 'Surface reconstruction failed. library failure'
    assert not anatomy_model.pending
    assert 'library failure' in anatomy_model.status_message(2)


def test_failed_outline_row_cannot_claim_visible_geometry(cylinder_window, anatomy_model):
    """Show an unchecked unavailable outline when a requested organ has no wire.

    A checked row or missing failure tooltip fails; an invisible organ must not
    appear successfully displayed beside the patient's probe.
    """
    from dataclasses import replace
    from PySide6.QtCore import Qt
    from windows.models.structures_model import StructureDisplayMode
    model = cylinder_window.structuresmodel
    model.set_mode(StructureDisplayMode.OUTLINES)
    plan = DicomData()
    plan.probe_frame_uid, plan.cylinder_base, plan.cylinder_direction = '1.2.3', (0., 0., 0.), (0., 0., 10.)
    plan.structures = (replace(anatomy_model.structures[2], contours=(Contour('CLOSED_PLANAR', ((0., 0., 2.),) * 3),)),)
    model.load_plan(plan, 20.)
    item = cylinder_window.navigationmodel.views[5].structure_list.item(0)
    assert item.checkState() == Qt.Unchecked
    assert not item.flags() & Qt.ItemIsUserCheckable or not item.flags() & Qt.ItemIsEnabled
    assert item.toolTip().startswith('Outline unavailable.')
