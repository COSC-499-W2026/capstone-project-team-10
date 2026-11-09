"""Exercise src/classes/mesh/tandem.py: the tandem channel cut out of the cylinder."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps

if TYPE_CHECKING:
    from OCC.Core.TopoDS import TopoDS_Shape

    from classes.mesh.tandem import Tandem
    from settings.tandem_templates import TandemDesign


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


def design(height_mm: float, bend_angle_deg: float = 30.0) -> TandemDesign:
    """Return the default Generate settings with the given height and bend, as a helper and not a test."""
    from settings.tandem_templates import TandemDesign

    return TandemDesign(height_mm, 3.8, 5.0, bend_angle_deg, 35.0, 7.0, 5.0, 0.0)


def test_a_tandem_is_built_from_every_design_value_and_the_cylinder(default_settings: dict[str, float]) -> None:
    """Check that tandem_from_design copies the eight settings, except rotation, and the cylinder into a Tandem.

    Fails if a value is dropped or read into the wrong attribute, which would make the trial
    build on Load check a different tandem from the one Generate Tandem builds.
    """
    from classes.mesh.tandem import tandem_from_design
    from settings.tandem_templates import TandemDesign

    tandem = tandem_from_design(TandemDesign(140.5, 4.2, 6.5, 45.0, 40.0, 8.0, 5.5, 258.697), 173.0, 31.25)

    assert (tandem.tandem_height, tandem.tandem_diameter, tandem.stopper_diameter, tandem.tandem_angle,
            tandem.bend_radius, tandem.threading_depth, tandem.threading_diameter,
            tandem.cylinder_height, tandem.cylinder_diameter) == (140.5, 4.2, 6.5, 45.0, 40.0, 8.0, 5.5, 173.0, 31.25)


@pytest.mark.parametrize("height_mm, bend_angle_deg, builds", [
    (120.0, 30.0, True),
    (60.0, 30.0, False),
    (170.0, 30.0, False),
    (60.0, 0.0, True),
])
def test_only_a_tandem_that_generate_can_build_is_buildable(
    default_settings: dict[str, float], height_mm: float, bend_angle_deg: float, builds: bool,
) -> None:
    """Check tandem_builds on a 160 by 30 mm cylinder: a 30 degree bend at 120 mm builds, at 60 or 170 mm it does not.

    At 60 mm the bend reaches the wall before the dome, and generate_shape raises "Tandem
    doesn't exit cylinder!". At 170 mm the bend starts above the cylinder. A straight tandem
    builds at 60 mm. Fails if a design Generate Tandem refuses is called buildable, or the other
    way round: Load would then say nothing about a template Generate will reject, or warn about
    one it builds.
    """
    from classes.mesh.tandem import tandem_builds, tandem_from_design

    assert tandem_builds(tandem_from_design(design(height_mm, bend_angle_deg), 160.0, 30.0)) is builds
