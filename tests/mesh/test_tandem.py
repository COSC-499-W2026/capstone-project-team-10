"""Exercise src/classes/mesh/tandem.py: the tandem channel cut out of the cylinder."""
from __future__ import annotations

from typing import TYPE_CHECKING

from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps

if TYPE_CHECKING:
    from OCC.Core.TopoDS import TopoDS_Shape

    from classes.mesh.tandem import Tandem


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in cubic millimetres, to 3 places.

    A helper, not a test.
    """
    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return round(properties.Mass(), 3)


def tandem_for(diameter: float, tandem_height: float) -> Tandem:
    """Return a Tandem for a cylinder of the given diameter, 160 mm long, from the live settings.

    A helper, not a test. Tandem Height is passed because the default, 170 mm, is taller than
    the cylinder and cannot be built (section 7.6 of the project docs).
    """
    from classes.mesh.tandem import Tandem

    tandem = Tandem()
    tandem.cylinder_diameter = diameter
    tandem.cylinder_height = 160.0
    tandem.tandem_height = tandem_height
    return tandem


def test_the_default_dome_tandem_cut_out_is_unchanged(default_settings: dict[str, float]) -> None:
    """Check the default tandem cut-out in a 30 mm dome cylinder still measures 3,875.268 mm^3.

    The literal was measured on the branch before the flat-tip fix. Fails if the fix changes
    a dome cylinder's tandem channel, which every existing design uses.
    """
    assert volume(tandem_for(30.0, 120.0).generate_shape()) == 3875.268


def test_a_flat_tip_keeps_all_of_the_tandem_cut_out_inside_the_cylinder(
    default_settings: dict[str, float],
) -> None:
    """Check no tandem cut-out inside a flat-tipped 90 mm cylinder is trimmed away.

    The cut-out is trimmed by an outline sized for a dome. A flat top's corners stick out of it
    once the diameter passes about 45 mm, so the trim removed up to 133 mm^3 of channel inside
    the cylinder at a 80 degree bend, leaving solid where the tandem must pass. Fails if any of
    the untrimmed cut-out that lies inside the cylinder is missing from the trimmed one.
    """
    from classes.mesh.cylinder import BrachyCylinder
    from classes.mesh.tandem import fuse_shapes

    default_settings["CONFIG_CYLINDER_FLAT_TIP"] = 1
    default_settings["CONFIG_NOTCH_ENABLED"] = 0
    cylinder = BrachyCylinder(diameter=90.0)
    cylinder.enableBase(False)
    tandem = tandem_for(90.0, 100.0)
    tandem.tandem_angle = 80
    untrimmed = fuse_shapes([tandem.tandem_tool_shape(), tandem.stopper_shape()])
    trimmed_away = BRepAlgoAPI_Cut(untrimmed, tandem.cylinder_offset_shape()).Shape()
    assert volume(BRepAlgoAPI_Common(trimmed_away, cylinder.shape()).Shape()) == 0.0
