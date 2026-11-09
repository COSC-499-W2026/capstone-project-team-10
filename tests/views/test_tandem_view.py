from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

if TYPE_CHECKING:
    from windows.main_window import MainWindow
    from windows.views.tandem_view import TandemView

CYLINDER_TAB = 1
TANDEM_TAB = 3
SETTING_THE_SNAPSHOT_OMITS = "CONFIG_FROM_A_NEWER_VERSION"


def test_generating_a_tandem_keeps_settings_the_snapshot_omits(cylinder_window: MainWindow) -> None:
    """Generate a tandem and check a setting getCurrentValues() does not list survives.

    Fails when Generate Tandem replaces the live settings with the snapshot instead of
    merging it in, which drops every key the snapshot leaves out. A dropped setting falls
    back to its default at the next rebuild, so the printed cylinder would quietly differ
    from the one the clinician designed. The collar was lost this way (section 7.1 of the
    project docs). Tandem Height is set to 120 mm because the default, 170 mm, is taller
    than the 160 mm cylinder and cannot be built.
    """
    from classes.app import get_app

    cylinder_window.navigationmodel.views[CYLINDER_TAB].action_apply_settings()
    get_app().values.config_values[SETTING_THE_SNAPSHOT_OMITS] = 1.0
    tandem_view = cylinder_window.navigationmodel.views[TANDEM_TAB]
    tandem_view.ui.sb_tandem_height.setValue(120)
    tandem_view.action_set_tandem()
    assert get_app().values.config_values.get(SETTING_THE_SNAPSHOT_OMITS) == 1.0


TYPED = (140.5, 4.2, 6.5, 45.0, 40.0)


def generate_typed_tandem(window: MainWindow) -> TandemView:
    """Type TYPED into Ex2's Generate boxes over the default settings and press Generate Tandem, as a helper and not a test.

    The live tandem settings are put back to the defaults first, a 170 mm Tandem Height taller
    than Ex2's 160 mm cylinder, as on a new plan, so no earlier Generate in the module hides the
    reset boxes. The rotation warning is marked as already shown, because it is a modal dialog no
    offscreen test can answer.
    """
    from classes.app import get_app
    from settings.defaults import DEFAULT_CONFIG_VALUES

    for key in ("CONFIG_TANDEM_TIP_HEIGHT", "CONFIG_TANDEM_CHANNEL_DIAMETER", "CONFIG_TANDEM_STOPPER_DIAMETER",
                "CONFIG_TANDEM_TIP_ANGLE", "CONFIG_TANDEM_BEND_RADIUS"):
        get_app().values.config_values[key] = DEFAULT_CONFIG_VALUES[key]
    view = window.navigationmodel.views[TANDEM_TAB]
    view.hasShownRotationWarning = True
    ui = view.ui
    for box, value in zip((ui.sb_tandem_height, ui.sp_channel_diameter, ui.sp_stopper_diameter,
                           ui.sp_bend_angle, ui.sb_bend_radius), TYPED):
        box.setValue(value)
    QTest.mouseClick(ui.btn_apply, Qt.MouseButton.LeftButton)
    return view


def built(window: MainWindow) -> tuple[float, ...]:
    """The height, diameters, bend angle and radius the tandem model built with, as a helper and not a test."""
    tandem = window.tandemmodel
    return (tandem.tandem_length, tandem.tandem_diameter, tandem.stopper_diameter, tandem.tip_angle, tandem.bend_radius)


def test_generate_shows_the_values_the_tandem_was_built_with(tandem_window: MainWindow) -> None:
    """Check that after Generate Tandem on Ex2 the boxes show 4.2 mm, 6.5 mm, 45 and 40 mm, the tandem that was cut.

    Generate tries each value on a tandem that starts from the live 170 mm height, which cannot
    be built, so each try failed and its box was put back to the default, while the final build
    used every typed value. Fails if a box shows 3.8, 5.0, 30 or 35 when the tandem was built
    with 4.2, 6.5, 45 and 40: the clinician would approve a device whose tandem hole differs
    from what the tab shows (section 7.23 of the project docs).
    """
    view = generate_typed_tandem(tandem_window)
    ui = view.ui

    shown = (ui.sb_tandem_height.value(), ui.sp_channel_diameter.value(), ui.sp_stopper_diameter.value(),
             ui.sp_bend_angle.value(), ui.sb_bend_radius.value())
    assert built(tandem_window) == TYPED
    assert shown == TYPED


def test_generating_again_keeps_the_tandem_that_was_typed(tandem_window: MainWindow) -> None:
    """Check that pressing Generate Tandem a second time, changing nothing, keeps the 4.2 mm, 45 degree tandem.

    Fails if the second Generate rebuilds from boxes that were put back to 3.8 mm and 30
    degrees, which changed the tandem cut into the cylinder with no warning, for instance when
    only the rotation was changed and the tandem regenerated.
    """
    view = generate_typed_tandem(tandem_window)

    QTest.mouseClick(view.ui.btn_apply, Qt.MouseButton.LeftButton)

    assert built(tandem_window) == TYPED
