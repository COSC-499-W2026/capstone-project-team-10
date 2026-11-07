"""Hidden organ surfaces remain available for non-display checks."""
from PySide6.QtTest import QTest


def organ_plan():
    """Build a square organ, a target and BODY sharing a literal probe frame.

    This helper supplies known tissue bounds; inclusion of BODY/target would
    cause the organ-only assertions to fail and flood the user with expected hits.
    """
    from classes.dicom.data import DicomData
    from classes.dicom.structures import Contour, Structure, StructureType
    plan = DicomData()
    plan.probe_frame_uid = 'test-frame'
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    contours = tuple(Contour('CLOSED_PLANAR', ((-2.,-2.,z),(2.,-2.,z),(2.,2.,z),(-2.,2.,z)))
                     for z in (4., 6., 8.))
    plan.structures = tuple(Structure(roi, name, 'test-frame', (0,255,0), kind, category, contours)
                           for roi, name, kind, category in (
                               (2,'Bladder','ORGAN',StructureType.ORGAN),
                               (3,'Target','PTV',StructureType.TUMOUR),
                               (4,'BODY','EXTERNAL',StructureType.OTHER)))
    return plan


def test_prepare_requests_hidden_outlines_organs(cylinder_window):
    """Request an organ surface even when its actor is hidden in Outlines mode.

    Returning only visible actors or including BODY and targets fails; collision
    callers need all eligible tissue independently of the display preference.
    """
    from windows.models.structures_model import StructureDisplayMode
    model = cylinder_window.structuresmodel
    model.set_mode(StructureDisplayMode.OUTLINES)
    model.load_plan(organ_plan(), 10.)
    model.set_visible(2, False)
    surfaces, unchecked = model.prepare_organ_collision_surfaces()
    assert not surfaces and set(unchecked) == {2}
    assert model.surface_pool.waitForDone(10000)
    QTest.qWait(1)
    surfaces, unchecked = model.prepare_organ_collision_surfaces()
    assert set(surfaces) == {2} and not unchecked
    assert 2 not in model.visible


def test_prepare_reports_wrong_frame_without_requesting_mesh(cylinder_window):
    """Refuse mismatched anatomy with an explicit unchecked reason and no job.

    Treating a different frame as usable or submitting reconstruction fails;
    geometry from another coordinate system must not produce clearance claims.
    """
    from dataclasses import replace
    model = cylinder_window.structuresmodel
    plan = organ_plan()
    plan.structures = (replace(plan.structures[0], frame_of_reference_uid='other'),)
    model.load_plan(plan, 10.)
    surfaces, unchecked = model.prepare_organ_collision_surfaces()
    assert not surfaces and set(unchecked) == {2}
    assert not model.pending


def test_snapshot_does_not_start_reconstruction(cylinder_window):
    """Read collision inputs without queuing work during a display notification.

    Starting a surface task fails the pending-set assertion; input comparison
    must not make a failed outline appear to be loading visible geometry.
    """
    from windows.models.structures_model import StructureDisplayMode
    model = cylinder_window.structuresmodel
    model.set_mode(StructureDisplayMode.OUTLINES)
    model.load_plan(organ_plan(), 10.)
    model.prepare_organ_collision_surfaces(request_missing=False)
    assert not model.pending
