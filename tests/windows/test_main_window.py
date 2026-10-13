from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest

if TYPE_CHECKING:
    from PySide6.QtWidgets import QPushButton

    from windows.main_window import MainWindow

IMPORT_TAB = 0
CYLINDER_TAB = 1
EXPORT_TAB = 4
SAMPLE_PLAN = Path(__file__).resolve().parents[2] / "SI_C_D30 Brachify_Ex1"
SELECTED_TAB_BACKGROUND = QColor(28, 44, 81)


def click(button: QPushButton) -> None:
    """Click a button with the left mouse button, the way a clinician does.

    A helper, not a test. QTest sends a real press and release, so the button emits pressed
    and every slot the window connected to it runs, including the navigation lambdas.
    """
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)


def apply_cylinder_settings(window: MainWindow) -> None:
    """Press Apply Settings on the Cylinder tab, which builds a cylinder with no plan imported.

    A helper, not a test. This is the only way to get a cylinder without a DICOM import today.
    """
    click(window.navigationmodel.views[CYLINDER_TAB].ui.btn_apply_settings)


def test_clicking_export_before_a_cylinder_exists_stays_on_the_import_tab(
    fresh_window: MainWindow,
) -> None:
    """Check that clicking Export before any cylinder exists leaves the Import tab showing.

    The Export tab builds its mesh from the cylinder, and there is none yet. Fails if the
    navigation model moved to the Export page or the screen changed page. Before the fix the
    click raised AttributeError inside Export_View._final_mesh after the navigation model had
    already recorded page 4, so the app believed it was on Export while the screen still showed
    Import, and a second click on Export then did nothing at all.
    """
    click(fresh_window.ui.btn_export_view)

    assert fresh_window.navigationmodel.current_page == IMPORT_TAB
    assert fresh_window.ui.viewswidget.currentIndex() == IMPORT_TAB


def test_export_button_looks_disabled_after_visiting_another_tab(fresh_window: MainWindow) -> None:
    """Check that the Export button is drawn differently while it cannot be used.

    Opens the Cylinder tab first, because every tab click rewrites every nav button's
    stylesheet, so a disabled look set only at start-up would be lost on the first click. Fails
    if the disabled Export button renders the same as an enabled one. The nav stylesheets have
    no disabled rule of their own, so without one a disabled button still looks clickable and
    the clinician cannot tell why clicking it does nothing.
    """
    click(fresh_window.ui.btn_cylinder_view)
    export_button = fresh_window.ui.btn_export_view
    disabled_look = export_button.grab().toImage()

    export_button.setEnabled(True)

    assert export_button.grab().toImage() != disabled_look


def test_export_tab_opens_once_cylinder_settings_are_applied(fresh_window: MainWindow) -> None:
    """Check that a cylinder made with Apply Settings alone, no plan imported, can be exported.

    Fails if the Export page is not showing after Apply Settings and a click on Export.
    Exporting a cylinder without a DICOM plan works today, and FR-CN-10 asks for designs that
    start without one, so guarding the Export tab must not lock this path out.
    """
    apply_cylinder_settings(fresh_window)

    click(fresh_window.ui.btn_export_view)

    assert fresh_window.ui.viewswidget.currentIndex() == EXPORT_TAB


def test_export_button_is_enabled_after_a_plan_is_imported(fresh_window: MainWindow) -> None:
    """Check that importing the Ex1 sample plan makes the Export button usable.

    The import reads the plan the way ImportView.action_import_dicom_folder does, minus the
    folder dialog. Fails if the Export button is still disabled afterwards, which would leave
    a clinician with an imported plan and no way back to the Export tab to save the model.
    """
    from classes.dicom.fileio import read_dicom_folder

    fresh_window.dicommodel.update(read_dicom_folder(str(SAMPLE_PLAN)))

    assert fresh_window.ui.btn_export_view.isEnabled()


def test_export_button_is_highlighted_after_opening_export_with_applied_settings(
    fresh_window: MainWindow,
) -> None:
    """Check that the Export button shows as the current tab when opened without a plan.

    Fails if the button's background is not the selected tab's dark blue, rgb(28, 44, 81),
    after Apply Settings and a click on Export. The highlight used to depend on a plan having
    been imported, so on this path the screen showed Export while the button bar still
    highlighted the Cylinder tab.
    """
    apply_cylinder_settings(fresh_window)
    export_button = fresh_window.ui.btn_export_view

    click(export_button)

    assert export_button.grab().toImage().pixelColor(2, 2) == SELECTED_TAB_BACKGROUND
