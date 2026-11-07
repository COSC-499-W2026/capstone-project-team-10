"""Real collision state follows geometry changes without involving warning widgets."""
from time import monotonic
import pytest
from PySide6.QtTest import QTest
from test_organ_collision_inputs import organ_plan


def wait_for_checks(window):
    """Helper delivering worker signals, failing after thirty seconds if checks stall.

    Waiting for both pools prevents treating an unfinished organ as collision-free.
    """
    deadline = monotonic() + 30
    while monotonic() < deadline:
        QTest.qWait(20)
        if (not window.structuresmodel.pending and not window.collisionmodel.busy
                and not window.collisionmodel.timer.isActive()):
            return
    pytest.fail('Organ collision checks did not finish')


def load_collision_scene(window):
    """Helper installing real needle paths and an organ without building channel solids.

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


def test_display_preferences_preserve_check_and_emphasis(cylinder_window):
    """Keep completed warnings and emphasis through selection and display changes.

    Invalidating on unchanged geometry fails the revision and highlight checks;
    browsing the plan must not erase a warning the user is investigating.
    """
    from windows.models.structures_model import StructureDisplayMode
    window = cylinder_window
    load_collision_scene(window)
    model = window.collisionmodel
    model.highlight(2)
    revision = model.revision
    window.channelsmodel.values_changed.emit()
    window.structuresmodel.set_visible(2, False)
    window.structuresmodel.set_mode(StructureDisplayMode.OUTLINES)
    assert model.revision == revision
    assert model.highlighted == ('Needle 1',)
    assert model.collisions == {2: ('Needle 1',)}


def test_failed_path_check_is_explicit_and_hides_exception_details(cylinder_window):
    """Report an unchecked organ when malformed settings raise a non-ValueError.

    An escaping TypeError or a raw exception in the user message fails; missing
    needle geometry cannot look like a completed clear check.
    """
    from classes.app import get_app
    window = cylinder_window
    load_collision_scene(window)
    get_app().values.config_values['CONFIG_DEADSPACE'] = None
    window.channelsmodel.values_changed.emit()
    window.collisionmodel.check()
    assert not window.collisionmodel.collisions
    assert 2 in window.collisionmodel.unchecked
    assert 'NoneType' not in window.collisionmodel.unchecked[2]
    get_app().values.config_values['CONFIG_DEADSPACE'] = 0.


def test_moving_needle_reuses_organ_index(cylinder_window):
    """Reuse the validated organ index when only a needle moves.

    Rebuilding the tissue search structure changes identity and fails; editing a
    needle should not repeat expensive organ alignment and topology checks.
    """
    window = cylinder_window
    load_collision_scene(window)
    indexed = window.collisionmodel.indexes[2]
    window.channelsmodel.channels['Needle 1'].set_translation((8.,0.,0.))
    window.channelsmodel.values_changed.emit()
    wait_for_checks(window)
    assert window.collisionmodel.indexes[2] is indexed
    assert window.collisionmodel.collisions == {}


def test_repeated_clear_does_not_emit_highlight_changes(cylinder_window):
    """Avoid unnecessary viewport redraws when emphasis is already cleared.

    An unconditional highlight signal fails the observed signal count; repeated
    notifications must not trigger full redraws without a changed selection.
    """
    from PySide6.QtTest import QSignalSpy
    model = cylinder_window.collisionmodel
    signals = QSignalSpy(model.highlight_changed)
    model.highlight(None)
    model.highlight(None)
    assert signals.count() == 0
