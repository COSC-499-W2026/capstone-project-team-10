"""Check that the mesh and the reference sheet follow a tandem template once it is loaded and generated."""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from OCC.Core.TopoDS import TopoDS_Shape

    from settings.tandem_templates import TandemDesign
    from windows.main_window import MainWindow
    from windows.views.tandem_view import TandemView

TANDEM_TAB = 3
EXPORT_TAB = 4
LONG_BEND = (140.5, 4.2, 6.5, 45.0, 40.0, 8.0, 5.5, 258.697)


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in cubic millimetres, as a helper and not a test."""
    from OCC.Core.BRepGProp import brepgprop
    from OCC.Core.GProp import GProp_GProps

    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return properties.Mass()


@pytest.fixture
def plan_tab(tandem_window: MainWindow) -> Iterator[TandemView]:
    """Give each test Ex2's Tandem tab with an empty library, the plan's own tandem channel and no tandem.

    A fixture, not a test. tandem_window is shared by the module, so the library is emptied, the
    tandem cleared and channel 14, Tandem, made the tandem channel before and after each test. The
    rotation warning is marked as already shown, because Generate Tandem asks it through a modal
    dialog no offscreen test can answer.
    """
    from classes.info import USER_PATH
    from settings.tandem_templates import LIBRARY_FILE_NAME

    library = USER_PATH / LIBRARY_FILE_NAME
    library.unlink(missing_ok=True)
    tandem_window.channelsmodel.set_tandem("Tandem")
    view = tandem_window.navigationmodel.views[TANDEM_TAB]
    view.hasShownRotationWarning = True
    view.action_load_templates()
    yield view
    library.unlink(missing_ok=True)
    tandem_window.tandemmodel.clear_tandem()
    tandem_window.channelsmodel.set_tandem("Tandem")


def load_and_generate(view: TandemView) -> TandemDesign:
    """Save LONG_BEND straight to the library, Load it and press Generate Tandem, as a helper and not a test.

    The Generate boxes are left at the defaults before Load, so a setting Load skipped would be
    built at its default and show in the exports. Returns the saved design.
    """
    from datetime import datetime, timezone

    from settings.tandem_templates import TandemDesign, add_template, make_template

    saved_at = datetime(2026, 11, 2, 17, 5, tzinfo=timezone.utc)
    design = TandemDesign(*LONG_BEND)
    add_template(view.templates_path, make_template("a1", "Export check", "", design, saved_at, saved_at))
    view.action_load_templates()
    view.ui.list_templates.setCurrentRow(0)
    view.action_load_template()
    view.action_set_tandem()
    return design


def cut_out(design: TandemDesign) -> TopoDS_Shape:
    """Build a design's tandem cut-out in Ex2's 160 by 30 mm cylinder, turned to its rotation, as a helper and not a test.

    It is built straight from classes.mesh.tandem, not through the Tandem tab, so it is an
    independent copy of what the template should cut.
    """
    from OCC.Core.gp import gp
    from OCC.Extend.ShapeFactory import rotate_shape

    from classes.mesh.tandem import tandem_from_design

    unturned = tandem_from_design(design, 160.0, 30.0).generate_shape()
    return rotate_shape(shape=unturned, axis=gp.OZ(), angle=design.rotation_deg)


def test_the_exported_mesh_has_the_templates_tandem_hole(tandem_window: MainWindow, plan_tab: TandemView) -> None:
    """Check that the Export tab's mesh of Ex2 has the loaded template's tandem cut out of it, and not the default one.

    The template's own cut-out, built independently and turned to 258.697 degrees, must leave no
    solid in the mesh, while the default 30 degree tandem aimed at 0 degrees crosses solid
    material. Fails if the mesh is cut with the defaults, an unrotated tandem, or no tandem. The
    STL is the device that is printed, so its tandem hole must be the template's.
    """
    from dataclasses import replace

    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common

    from classes.app import get_app

    design = load_and_generate(plan_tab)

    get_app().signals.viewChanged.emit(EXPORT_TAB)
    mesh = tandem_window.navigationmodel.views[EXPORT_TAB].shape
    default = replace(design, height_mm=120.0, channel_diameter_mm=3.8, stopper_diameter_mm=5.0,
                      bend_angle_deg=30.0, bend_radius_mm=35.0, rotation_deg=0.0)

    assert volume(BRepAlgoAPI_Common(mesh, cut_out(design)).Shape()) == pytest.approx(0.0, abs=0.5)
    assert volume(BRepAlgoAPI_Common(mesh, cut_out(default)).Shape()) > 100.0


def test_the_reference_sheet_draws_the_templates_tandem(tandem_window: MainWindow, plan_tab: TandemView) -> None:
    """Check the two values the reference sheet draws the tandem from after the template is generated.

    save_points_diagram draws the tandem circle at the live CONFIG_TANDEM_CHANNEL_DIAMETER and its
    dashed direction line at the rotation the Export tab passes, TandemModel.rotation. Fails if
    either is still the default, 3.8 mm or 0 degrees. The sheet is how the tandem is aimed in
    the clinic, so a line drawn at the old direction would point the bend the wrong way.
    """
    from classes.app import get_app

    load_and_generate(plan_tab)

    assert get_app().values.config_values["CONFIG_TANDEM_CHANNEL_DIAMETER"] == 4.2
    assert tandem_window.tandemmodel.rotation == 258.697
    assert tandem_window.tandemmodel.shape() is not None
