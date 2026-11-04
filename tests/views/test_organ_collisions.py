"""Warnings follow real model edits without initializing the native viewport."""
from time import monotonic, sleep
import pytest
from PySide6.QtCore import Qt, QPoint
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


def wait_for_checks(window):
    """Deliver actual worker signals, failing after ten seconds if checks stall.

    Waiting for both pools prevents treating an unfinished organ as collision-free.
    """
    deadline = monotonic() + 10
    while monotonic() < deadline:
        QTest.qWait(20)
        sleep(0.001)
        if (not window.structuresmodel.pending and not window.collisionmodel.busy
                and not window.collisionmodel.timer.isActive()):
            return
    pytest.fail('Organ collision checks did not finish')


def load_collision_scene(window):
    """Install two real needle paths and an organ without building channel solids.

    The first needle crosses the organ; the second misses. Model warnings must
    identify only the first or the integration assertions fail.
    """
    from classes.mesh.channel import NeedleChannel
    from classes.app import get_app
    get_app().values.config_values['CONFIG_DEADSPACE'] = 0.
    window.channelsmodel.channels = {
        'Needle 1': NeedleChannel('10','1','Needle 1', [[0.,0.,12.],[0.,0.,0.]]),
        'Needle 2': NeedleChannel('11','2','Needle 2', [[8.,0.,12.],[8.,0.,0.]])}
    window.structuresmodel.load_plan(organ_plan(), 10.)
    wait_for_checks(window)


def test_warning_click_shows_toast_and_highlights_only_colliding_needles(cylinder_window):
    """Click the red warning area, producing a toast and the correct red selection.

    Wrong ROI mapping, an inert warning or highlighting unrelated needles fails;
    the user must be able to identify which needle may contact the organ.
    """
    window = cylinder_window
    load_collision_scene(window)
    assert window.collisionmodel.collisions == {2: ('Needle 1',)}
    view = window.navigationmodel.views[5]
    view.resize(350, 500)
    view.show()
    item = view.structure_list.item(0)
    assert item.data(Qt.UserRole + 1) == ('Needle 1',)
    rect = view.structure_list.visualItemRect(item)
    QTest.mouseClick(view.structure_list.viewport(), Qt.LeftButton, pos=rect.topRight() + QPoint(-12, rect.height() // 2))
    assert 'Possible collision detected' in view.collision_toast.text()
    assert 'Needle 1' in view.collision_toast.text()
    assert not view.collision_toast.isHidden()
    assert window.collisionmodel.highlighted == ('Needle 1',)
    view.on_close()
    assert window.collisionmodel.highlighted == ()
    assert view.collision_toast.isHidden()
    view.structure_list.setCurrentRow(0)
    QTest.keyClick(view.structure_list, Qt.Key_Return)
    assert window.collisionmodel.highlighted == ('Needle 1',)


def test_move_disable_hide_and_reset_invalidate_collision_state(cylinder_window):
    """Recheck moved/disabled needles while keeping hidden organs checked; reset clears.

    Stale warnings or red selections, or hiding an organ suppressing its warning,
    fail and would misrepresent the current plan after editing.
    """
    window = cylinder_window
    load_collision_scene(window)
    window.structuresmodel.set_visible(2, False)
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {2: ('Needle 1',)}
    window.collisionmodel.highlight(2)
    window.channelsmodel.channels['Needle 1'].set_translation((8.,0.,0.))
    window.channelsmodel.values_changed.emit()
    assert window.collisionmodel.highlighted == ()
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {}
    window.channelsmodel.channels['Needle 1'].set_translation((0.,0.,0.))
    window.channelsmodel.disabled_channels = ['Needle 1']
    window.channelsmodel.values_changed.emit()
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {}
    window.channelsmodel.disabled_channels = []
    window.channelsmodel.values_changed.emit()
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {2: ('Needle 1',)}
    window.structuresmodel.clear()
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {}


def test_unavailable_geometry_is_reported_and_stale_results_are_rejected(cylinder_window):
    """Reject old worker results after reset and explicitly show uncheckable anatomy.

    Accepting an old hit or showing an unchecked organ as clear fails; stale
    results must never identify a needle from another plan.
    """
    from dataclasses import replace
    from windows.models.collision_model import CollisionResult
    window = cylinder_window
    load_collision_scene(window)
    revision = window.collisionmodel.revision
    window.structuresmodel.clear()
    window.collisionmodel.accept(CollisionResult(revision, {2: ('Needle 1',)}))
    assert window.collisionmodel.collisions == {}
    plan = organ_plan()
    plan.structures = (replace(plan.structures[0], frame_of_reference_uid='wrong'),)
    window.structuresmodel.load_plan(plan, 10.)
    wait_for_checks(window)
    assert 2 in window.collisionmodel.unchecked
    assert 'not checked' in window.navigationmodel.views[5].collision_status.text().lower()


def test_collision_actor_is_red_opaque_and_above_the_probe(units_app):
    """Use a real red actor so the affected needle remains visible through the probe.

    A default colour, transparent material or ordinary depth layer fails; storing
    warning labels alone must not substitute for the promised visible emphasis.
    """
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
    from windows.views.viewport import collision_needle_presentation
    actor = collision_needle_presentation(BRepPrimAPI_MakeBox(1.,1.,4.).Shape())
    colour = actor.Attributes().ShadingAspect().Color()
    assert (colour.Red(), colour.Green(), colour.Blue()) == (1., 0., 0.)
    assert actor.Transparency() == 0.
    assert actor.ZLayer() == -3


def test_outlines_mode_and_length_change_keep_organ_checks(cylinder_window):
    """Check hidden organ surfaces in Outlines mode and align them after a length change.

    Depending on visible mesh actors or forgetting the length transform fails;
    a display preference must not suppress anatomical collision warnings.
    """
    from windows.models.structures_model import StructureDisplayMode
    window = cylinder_window
    window.structuresmodel.set_mode(StructureDisplayMode.OUTLINES)
    load_collision_scene(window)
    assert window.collisionmodel.collisions == {2: ('Needle 1',)}
    window.structuresmodel.set_length(30.)
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {}
    window.channelsmodel.channels['Needle 1'].set_offset(20.)
    window.channelsmodel.values_changed.emit()
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {2: ('Needle 1',)}


def test_diameter_deadspace_and_tandem_are_reflected_in_check_paths(cylinder_window):
    """Use edited radii and dead space while excluding the disabled tandem path.

    Missing tip extension, offsets or per-channel radius fails these literal path
    checks; using stale plan points would test a different needle than the preview.
    """
    from classes.app import get_app
    window = cylinder_window
    load_collision_scene(window)
    get_app().values.config_values['CONFIG_DEADSPACE'] = 2.
    channel = window.channelsmodel.channels['Needle 1']
    channel.set_diameter(3.6)
    channel.set_translation((1.,2.,3.))
    window.channelsmodel.disabled_channels = ['Needle 2']
    paths = window.collisionmodel.paths()
    assert len(paths) == 1
    assert paths[0].points == ((1.,2.,17.), (1.,2.,3.), (1.,2.,-1.))
    assert paths[0].radius == 1.8


def test_generated_shaft_extension_is_checked(cylinder_window):
    """Include the vertical shaft Brachify generates below the last path point.

    Ignoring this extension misses the organ below both imported dwell points
    and fails; the displayed needle shaft must not silently escape the check.
    """
    from classes.mesh.channel import NeedleChannel
    window = cylinder_window
    load_collision_scene(window)
    window.channelsmodel.channels = {
        'short path': NeedleChannel('10','1','short path', [[0.,0.,15.],[0.,0.,12.]])}
    window.channelsmodel.values_changed.emit()
    wait_for_checks(window)
    assert window.collisionmodel.collisions == {2: ('short path',)}
