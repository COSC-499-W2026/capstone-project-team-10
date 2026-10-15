"""Exercise src/classes/mesh/cylinder.py: the solid cylinder BrachyCylinder builds."""
from __future__ import annotations

from typing import TYPE_CHECKING

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.GProp import GProp_GProps
from OCC.Core.gp import gp_Pnt

if TYPE_CHECKING:
    from OCC.Core.TopoDS import TopoDS_Shape

DIAMETER = 30.0


def extents(solid: TopoDS_Shape) -> list[float]:
    """Return a solid's bounding box as [xmin, ymin, zmin, xmax, ymax, zmax], to 4 places.

    A helper, not a test. The box is measured without the default gap, so the tests compare
    against hand-worked literals.
    """
    box = Bnd_Box()
    box.SetGap(0)
    brepbndlib.Add(solid, box, False)
    return [round(value, 4) for value in box.Get()]


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in cubic millimetres, to 3 places.

    A helper, not a test. Two solids with the same volume to 3 places are, for these tests,
    the same solid.
    """
    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return round(properties.Mass(), 3)


def build_cylinder(collar: bool = False) -> TopoDS_Shape:
    """Build a 30 mm by 160 mm BrachyCylinder from the live settings and return its solid.

    A helper, not a test. enableBase is the setter the Cylinder tab's Apply calls, and it
    builds and stores the solid.
    """
    from classes.mesh.cylinder import BrachyCylinder

    cylinder = BrachyCylinder(diameter=DIAMETER)
    cylinder.enableBase(collar)
    return cylinder.shape()


def test_default_settings_build_the_cylinder_brachify_always_made(
    default_settings: dict[str, float],
) -> None:
    """Check the default cylinder keeps today's volume and its notch 1.8 mm out at -y.

    The literals were measured on main before notch settings existed. Fails if the defaults
    change the solid in any way, which would change every cylinder printed without anyone
    touching a setting.
    """
    solid = build_cylinder()
    assert volume(solid) == 109599.266
    assert extents(solid) == [-15.0, -16.8, 0.0, 15.0, 15.0, 160.0]


def test_a_disabled_notch_leaves_a_plain_cylinder(default_settings: dict[str, float]) -> None:
    """Check that with the notch turned off nothing sticks out of the 30 mm wall.

    Fails if the notch is still fused on, so the clinician would get an orientation mark
    they turned off.
    """
    default_settings["CONFIG_NOTCH_ENABLED"] = 0
    assert extents(build_cylinder()) == [-15.0, -15.0, 0.0, 15.0, 15.0, 160.0]


def test_the_notch_angle_setting_moves_the_notch(default_settings: dict[str, float]) -> None:
    """Check sheet angle 90 from the live settings moves the notch to the cylinder's +x side.

    Fails if BrachyCylinder ignores the angle setting, so the mark would stay at Anterior
    whatever the clinician chose.
    """
    default_settings["CONFIG_NOTCH_ANGLE"] = 90.0
    assert extents(build_cylinder()) == [-15.0, -15.0, 0.0, 16.8, 15.0, 160.0]


def test_a_collar_caps_the_notch_at_the_collar_height(default_settings: dict[str, float]) -> None:
    """Check a 20 mm notch on a 5 mm collar stops at the collar's top.

    With a collar the notch sits on the collar's outer wall, 18 mm from the axis here. Above
    the collar that wall ends, so a taller notch would stand free of the cylinder. The test
    intersects the solid with a probe box outside the collar, from 6 mm to 19 mm up, where
    an uncapped notch would be. Fails if anything of the notch is found there.
    """
    default_settings["CONFIG_NOTCH_HEIGHT"] = 20.0
    default_settings["CONFIG_BASE_THICKNESS"] = 3.0
    default_settings["CONFIG_BASE_HEIGHT"] = 5.0
    probe = BRepPrimAPI_MakeBox(gp_Pnt(-5.0, -25.0, 6.0), gp_Pnt(5.0, -18.5, 19.0)).Shape()
    assert volume(BRepAlgoAPI_Common(build_cylinder(collar=True), probe).Shape()) == 0.0


def test_a_notch_shorter_than_the_collar_keeps_its_own_height(
    default_settings: dict[str, float],
) -> None:
    """Check an 8 mm notch on a 20 mm collar stops at 8 mm, not at the collar's top.

    The probe box sits outside the 18 mm collar wall from 8.5 mm to 19 mm up. Fails if the
    notch height setting is ignored and the notch keeps a fixed height, so the clinician's
    shorter mark would print taller than chosen.
    """
    default_settings["CONFIG_NOTCH_HEIGHT"] = 8.0
    default_settings["CONFIG_BASE_THICKNESS"] = 3.0
    default_settings["CONFIG_BASE_HEIGHT"] = 20.0
    probe = BRepPrimAPI_MakeBox(gp_Pnt(-5.0, -25.0, 8.5), gp_Pnt(5.0, -18.5, 19.0)).Shape()
    assert volume(BRepAlgoAPI_Common(build_cylinder(collar=True), probe).Shape()) == 0.0
