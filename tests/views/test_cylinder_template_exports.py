"""Check that the mesh and the reference sheet follow a cylinder template once it is loaded and applied."""
from __future__ import annotations

from collections.abc import Iterator
from math import pi
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from OCC.Core.TopoDS import TopoDS_Shape

    from windows.main_window import MainWindow
    from windows.views.cylinder_view import CylinderView

CYLINDER_TAB = 1
EXPORT_TAB = 4
SAMPLE_PLAN = Path(__file__).resolve().parents[2] / "SI_C_D30 Brachify_Ex1"


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in cubic millimetres, as a helper and not a test."""
    from OCC.Core.BRepGProp import brepgprop
    from OCC.Core.GProp import GProp_GProps

    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return properties.Mass()


@pytest.fixture
def cylinder_tab(cylinder_window: MainWindow) -> Iterator[CylinderView]:
    """Give each test the real Cylinder tab with an empty template library.

    A fixture, not a test. The library file outlives a window, so it is deleted before and
    after each test, so no test sees another test's templates.
    """
    from classes.info import USER_PATH
    from settings.cylinder_templates import LIBRARY_FILE_NAME

    library = USER_PATH / LIBRARY_FILE_NAME
    library.unlink(missing_ok=True)
    view = cylinder_window.navigationmodel.views[CYLINDER_TAB]
    view.action_load_templates()
    yield view
    library.unlink(missing_ok=True)


def load_and_apply(view: CylinderView, design_values: tuple[float | bool, ...]) -> None:
    """Save a template straight to the library, then Load it and press Apply Settings, as a helper and not a test.

    The tab is left on the default cylinder before Load, so a setting Load skipped would be
    built at its default and show in the exports.
    """
    from datetime import datetime, timezone

    from settings.cylinder_templates import CylinderDesign, add_template, make_template

    saved_at = datetime(2026, 10, 19, 17, 5, tzinfo=timezone.utc)
    template = make_template("a1", "Export check", "", CylinderDesign(*design_values), saved_at, saved_at)
    add_template(view.templates_path, template)
    view.action_load_templates()
    view.ui.list_templates.setCurrentRow(0)
    view.action_load_template()
    view.action_apply_settings()


FLAT_COLLARED = (30.0, 160.0, True, 3.0, 10.0, False, 0.0, 2.0, 1.8, 10.0, True)


def test_the_reference_sheet_table_shows_the_loaded_template(
    cylinder_window: MainWindow, cylinder_tab: CylinderView,
) -> None:
    """Check the reference sheet's cylinder table after a flat, notch-off, 3 by 10 mm collar template is applied.

    Fails if any row still shows the default cylinder: a dome, a notch, or no collar. The QA
    team checks the printed cylinder against this table, so it must describe the template the
    physicist loaded (FR-CN-07).
    """
    from classes.pdf.template_reference import cylinder_rows

    load_and_apply(cylinder_tab, FLAT_COLLARED)

    assert cylinder_rows(cylinder_window.cylindermodel.cylinder) == [
        ["Diameter", "30.0 mm"],
        ["Length", "160.0 mm"],
        ["Tip", "Flat"],
        ["Notch", "Off"],
        ["Collar", "3.0 mm thick, 10.0 mm high"],
    ]


def test_the_exported_mesh_is_the_loaded_templates_cylinder(
    cylinder_window: MainWindow, cylinder_tab: CylinderView,
) -> None:
    """Check the Export tab's mesh volume after the same template is applied, with no plan imported.

    Worked by hand: a flat 30 by 160 mm cylinder is pi * 15^2 * 160 = 113,097.34 mm^3, and a
    collar 3 mm thick and 10 mm high adds pi * (18^2 - 15^2) * 10 = 3,110.18 mm^3, with no notch.
    Fails if the mesh is built with a dome, a notch, or no collar, all of which change the
    volume. The STL is the device that is printed, so it must be the template's cylinder.
    """
    from classes.app import get_app

    load_and_apply(cylinder_tab, FLAT_COLLARED)

    get_app().signals.viewChanged.emit(EXPORT_TAB)
    mesh = cylinder_window.navigationmodel.views[EXPORT_TAB].shape

    assert volume(mesh) == pytest.approx(pi * 15 ** 2 * 160 + pi * (18 ** 2 - 15 ** 2) * 10, abs=0.01)


def test_a_longer_template_moves_the_imported_needles_with_the_tip(
    cylinder_window: MainWindow, cylinder_tab: CylinderView,
) -> None:
    """Check that applying a 180 mm template to Ex1, imported at 160 mm, raises every needle 20 mm.

    Fails if a needle is not raised by exactly the change in length, or if its stored DICOM
    points change. Needles are positioned from the tip, so a longer cylinder must carry them up
    with it, or the printed channels would no longer meet the planned positions.
    """
    from classes.dicom.fileio import read_dicom_folder

    cylinder_window.cylindermodel.starting_length = 160.0
    cylinder_window.dicommodel.update(read_dicom_folder(str(SAMPLE_PLAN)))
    channels = cylinder_window.channelsmodel.get_visible_channels()
    stored = [[list(point) for point in channel.points] for channel in channels]
    tips_before = [channel.get_points()[0][2] for channel in channels]

    load_and_apply(cylinder_tab, (30.0, 180.0, False, 0.0, 0.0, True, 0.0, 2.0, 1.8, 10.0, False))

    assert [channel.get_points()[0][2] for channel in channels] == pytest.approx([z + 20.0 for z in tips_before])
    assert [[list(point) for point in channel.points] for channel in channels] == stored
    assert cylinder_window.cylindermodel.cylinder.length == 180.0
