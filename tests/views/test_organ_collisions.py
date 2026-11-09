"""Warning widgets and red actors identify affected needles without native canvas startup."""
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from test_organ_collision_inputs import organ_plan
from test_collision_model import load_collision_scene, wait_for_checks


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


def test_no_organs_status_does_not_imply_clearance(cylinder_window):
    """Explain that a plan without ORGAN entries has no organs eligible for checks.

    A generic completed-check message fails; excluded BODY and targets must not
    make an unexamined plan look clear.
    """
    plan = organ_plan()
    plan.structures = plan.structures[1:]
    cylinder_window.structuresmodel.load_plan(plan, 10.)
    wait_for_checks(cylinder_window)
    assert 'No organs to check' in cylinder_window.navigationmodel.views[5].collision_status.text()


def test_warning_copy_and_toggle_are_clear(cylinder_window):
    """Use readable warning copy and let the same warning clear red emphasis.

    Colons in the supplied copy or an emphasis that cannot be toggled off fail;
    users must understand and dismiss the temporary warning emphasis.
    """
    window = cylinder_window
    load_collision_scene(window)
    view = window.navigationmodel.views[5]
    view.show_collision(2)
    assert ':' not in view.collision_toast.text()
    assert ':' not in view.structure_list.item(0).toolTip()
    view.show_collision(2)
    assert not window.collisionmodel.highlighted
    assert view.collision_toast.isHidden()


def test_warning_hit_area_scales_with_list_font(units_app):
    """Keep the warning clickable when the list uses a larger accessibility font.

    A fixed pixel strip fails the width comparison; the warning must not shrink
    relative to enlarged text or overlap the organ name.
    """
    from PySide6.QtGui import QFont, QFontMetrics
    from PySide6.QtWidgets import QStyleOptionViewItem
    from PySide6.QtCore import QRect
    from windows.views.structures_view import CollisionWarningDelegate
    normal, large = QStyleOptionViewItem(), QStyleOptionViewItem()
    normal.rect = large.rect = QRect(0, 0, 300, 60)
    normal.fontMetrics = QFontMetrics(QFont('Arial', 10))
    large.fontMetrics = QFontMetrics(QFont('Arial', 24))
    assert CollisionWarningDelegate.warning_rect(large).width() > CollisionWarningDelegate.warning_rect(normal).width()


def test_background_check_does_not_mark_failed_outline_visible(cylinder_window):
    """Keep a failed outline unchecked while collision reconstruction is pending.

    Using any pending worker as proof of displayed geometry fails; background
    checks must not turn an invisible invalid organ into a checked display row.
    """
    from dataclasses import replace
    from classes.dicom.structures import Contour
    from windows.models.structures_model import StructureDisplayMode
    model = cylinder_window.structuresmodel
    model.set_mode(StructureDisplayMode.OUTLINES)
    plan = organ_plan()
    plan.structures = (replace(plan.structures[0], contours=(Contour('CLOSED_PLANAR', ((0.,0.,2.),)*3),)),)
    model.load_plan(plan, 10.)
    model.prepare_organ_collision_surfaces()
    view = cylinder_window.navigationmodel.views[5]
    view.action_update_structure_list()
    assert view.structure_list.item(0).checkState() == Qt.Unchecked


def test_switching_organs_with_same_needle_keeps_emphasis(cylinder_window):
    """Keep emphasis when a different organ warning names the same needle.

    Comparing only needle labels clears the second organ's warning and fails;
    only activating the same organ warning twice should toggle emphasis off.
    """
    from dataclasses import replace
    window = cylinder_window
    load_collision_scene(window)
    plan = organ_plan()
    plan.structures += (replace(plan.structures[0], roi_number=5, name='Rectum'),)
    window.structuresmodel.load_plan(plan, 10.)
    wait_for_checks(window)
    view = window.navigationmodel.views[5]
    view.show_collision(2)
    view.show_collision(5)
    assert window.collisionmodel.highlighted == ('Needle 1',)
    view.show_collision(5)
    assert window.collisionmodel.highlighted == ()
