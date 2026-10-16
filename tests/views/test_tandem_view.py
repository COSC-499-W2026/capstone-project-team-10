from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from windows.main_window import MainWindow

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
