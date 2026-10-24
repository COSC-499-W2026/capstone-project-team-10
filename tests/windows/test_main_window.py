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
STRUCTURES_TAB = 5
SAMPLE_PLAN = Path(__file__).resolve().parents[2] / "SI_C_D30 Brachify_Ex1"
SELECTED_TAB_BACKGROUND = QColor(28, 44, 81)
UNSELECTED_TAB_BACKGROUND = QColor(199, 219, 237)


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


def test_structures_view_is_appended_so_cylinder_and_export_keep_their_indexes(
    fresh_window: MainWindow,
) -> None:
    """Check that Structures is views[5] and Cylinder and Export did not move.

    Fails if views[5] is missing or is not a StructuresView, or if Cylinder left index 1 or
    Export left index 4. Inserting Structures after Import would shift every later tab and
    send cylinder length and tandem caps to the wrong widgets.
    """
    from windows.views.cylinder_view import CylinderView
    from windows.views.export_view import Export_View
    from windows.views.structures_view import StructuresView

    assert type(fresh_window.navigationmodel.views[STRUCTURES_TAB]) is StructuresView
    assert type(fresh_window.navigationmodel.views[CYLINDER_TAB]) is CylinderView
    assert type(fresh_window.navigationmodel.views[EXPORT_TAB]) is Export_View


def test_opening_structures_by_signal_shows_page_five(fresh_window: MainWindow) -> None:
    """Check that viewChanged(5) shows the Structures page.

    Fails if the stacked widget stays on Import, or if page 5 is not a StructuresView. There
    is no nav button yet, so a later tab that emits 5 is how a physicist will reach organs.
    """
    from classes.app import get_app
    from windows.views.structures_view import StructuresView

    get_app().signals.viewChanged.emit(STRUCTURES_TAB)

    assert fresh_window.navigationmodel.current_page == STRUCTURES_TAB
    assert fresh_window.ui.viewswidget.currentIndex() == STRUCTURES_TAB
    assert type(fresh_window.navigationmodel.views[STRUCTURES_TAB]) is StructuresView


def test_structures_button_sits_directly_under_import(fresh_window: MainWindow) -> None:
    """Check that Structures is the nav button immediately under Import.

    Fails if the button is missing, not labelled Structures, or sits anywhere else in the
    left bar. FR-SV needs its own page under Import, and a physicist looking for organs
    would open Cylinder if this button were below that instead.
    """
    layout = fresh_window.ui.verticalLayout_31
    import_index = layout.indexOf(fresh_window.ui.btn_import_view)
    structures_index = layout.indexOf(fresh_window.ui.btn_structures_view)

    assert fresh_window.ui.btn_structures_view.text() == "Structures"
    assert structures_index == import_index + 1


def test_clicking_structures_opens_the_structures_page_and_leaves_cylinder_at_one(
    fresh_window: MainWindow,
) -> None:
    """Check that Structures opens its own page and Cylinder stays views[1].

    Fails if the click does not show page 5, if that page is not a StructuresView, or if
    Cylinder or Export moved. Inserting Structures at index 1 would shift every later tab
    and send cylinder length and tandem caps to the wrong widgets.
    """
    from windows.views.cylinder_view import CylinderView
    from windows.views.export_view import Export_View
    from windows.views.structures_view import StructuresView

    click(fresh_window.ui.btn_structures_view)

    assert fresh_window.navigationmodel.current_page == STRUCTURES_TAB
    assert fresh_window.ui.viewswidget.currentIndex() == STRUCTURES_TAB
    assert type(fresh_window.navigationmodel.views[STRUCTURES_TAB]) is StructuresView
    assert type(fresh_window.navigationmodel.views[CYLINDER_TAB]) is CylinderView
    assert type(fresh_window.navigationmodel.views[EXPORT_TAB]) is Export_View


def test_clicking_cylinder_after_structures_still_opens_cylinder(fresh_window: MainWindow) -> None:
    """Check that Cylinder still opens after visiting Structures.

    Fails if the Cylinder click leaves the Structures page showing, or if views[1] is no
    longer Cylinder. A shifted index would make Apply Settings write into the wrong tab.
    """
    click(fresh_window.ui.btn_structures_view)
    click(fresh_window.ui.btn_cylinder_view)

    assert fresh_window.navigationmodel.current_page == CYLINDER_TAB
    assert fresh_window.ui.viewswidget.currentIndex() == CYLINDER_TAB
    assert fresh_window.ui.btn_cylinder_view.grab().toImage().pixelColor(2, 2) == SELECTED_TAB_BACKGROUND


def test_nav_buttons_do_not_overlap_after_show(fresh_window: MainWindow) -> None:
    """Check that the six nav buttons sit in separate rectangles inside the bar.

    Fails if any two button geometries overlap, or if a button extends past top_menu_bar,
    after show(). The bar's 165 px minimum is five 33 px rows, so a sixth button was drawn
    over Export and clipped. A physicist then cannot click Export cleanly.
    """
    from PySide6.QtWidgets import QApplication

    fresh_window.show()
    QApplication.processEvents()

    bar_rect = fresh_window.ui.top_menu_bar.rect()
    rectangles = [
        fresh_window.ui.btn_import_view.geometry(),
        fresh_window.ui.btn_structures_view.geometry(),
        fresh_window.ui.btn_cylinder_view.geometry(),
        fresh_window.ui.btn_channels_view.geometry(),
        fresh_window.ui.btn_tandem_view.geometry(),
        fresh_window.ui.btn_export_view.geometry(),
    ]

    for rectangle in rectangles:
        assert bar_rect.contains(rectangle)
    for index, first in enumerate(rectangles):
        for second in rectangles[index + 1 :]:
            assert not first.intersects(second)


def test_clicking_structures_highlights_structures_not_import(
    fresh_window: MainWindow,
) -> None:
    """Check that Structures is drawn selected and Import is not, after a Structures click.

    Fails if Structures's pixel is not rgb(28, 44, 81), or Import's still is. Dropping
    Structures from `_nav_buttons` left it unhighlighted and every other test still passed,
    so a physicist could be on the organs page with Import still looking current.
    """
    click(fresh_window.ui.btn_structures_view)

    assert (
        fresh_window.ui.btn_structures_view.grab().toImage().pixelColor(2, 2)
        == SELECTED_TAB_BACKGROUND
    )
    assert (
        fresh_window.ui.btn_import_view.grab().toImage().pixelColor(2, 2)
        != SELECTED_TAB_BACKGROUND
    )


def test_clicking_cylinder_after_structures_unhighlights_structures(
    fresh_window: MainWindow,
) -> None:
    """Check that Structures goes back to the unselected colour after Cylinder is clicked.

    Fails if Structures's pixel is not rgb(199, 219, 237). Disconnecting its colour slot
    left the previous tab highlighted, so the bar would still show Structures as current
    after the physicist had moved on.
    """
    click(fresh_window.ui.btn_structures_view)
    click(fresh_window.ui.btn_cylinder_view)

    assert (
        fresh_window.ui.btn_structures_view.grab().toImage().pixelColor(2, 2)
        == UNSELECTED_TAB_BACKGROUND
    )
