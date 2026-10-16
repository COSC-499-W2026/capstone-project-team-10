"""Exercise src/classes/mesh/notch.py: the orientation notch's size, position and settings."""
from __future__ import annotations

import pytest
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.TopoDS import TopoDS_Shape

from classes.mesh.notch import CylinderNotch, NotchSettings, notch_settings_from_config

DIAMETER = 30.0


def extents(solid: TopoDS_Shape) -> list[float]:
    """Return a solid's bounding box as [xmin, ymin, zmin, xmax, ymax, zmax], to 4 places.

    A helper, not a test. The box is measured without the default gap, so a 2 mm wide notch
    reads 2 mm wide and the tests can compare against hand-worked literals.
    """
    box = Bnd_Box()
    box.SetGap(0)
    brepbndlib.Add(solid, box, False)
    return [round(value, 4) for value in box.Get()]


def test_default_settings_build_the_notch_brachify_always_made() -> None:
    """Check the default notch is 2 mm wide, stands 1.8 mm out of a 30 mm wall, 10 mm tall, at Anterior.

    Fails if a default changes the notch. Before notch settings existed every cylinder had this
    notch, at model angle 270 degrees, the side the reference sheet labels Anterior. A different
    default would print every new cylinder with a moved or resized orientation mark.
    """
    notch = CylinderNotch(DIAMETER, NotchSettings(), 10.0)
    assert extents(notch.shape()) == [-1.0, -16.8, 0.0, 1.0, -14.8, 10.0]


def test_a_quarter_turn_clockwise_on_the_sheet_moves_the_notch_to_plus_x() -> None:
    """Check sheet angle 90 puts the notch on the model's +x side.

    The reference sheet looks up from the base with y drawn negated, so a quarter turn
    clockwise from Anterior on paper is the model's +x axis. Fails if the angle is applied in
    the model's own frame or the wrong way round, which would print the mark where the sheet
    says it is not, and the cylinder would be inserted with the needles rotated.
    """
    notch = CylinderNotch(DIAMETER, NotchSettings(angle=90.0), 10.0)
    assert extents(notch.shape()) == [14.8, -1.0, 0.0, 16.8, 1.0, 10.0]


def test_width_depth_and_height_size_the_notch() -> None:
    """Check a 4 mm wide, 3 mm deep, 20 mm tall notch at Anterior has exactly those extents.

    Depth is measured from the cylinder wall outward, and the box starts 0.2 mm inside the wall
    so it fuses to it. Fails if a dimension is ignored or swapped, which would print a mark of
    a size the clinician did not choose.
    """
    settings = NotchSettings(width=4.0, depth=3.0, height=20.0)
    notch = CylinderNotch(DIAMETER, settings, settings.height)
    assert extents(notch.shape()) == [-2.0, -18.0, 0.0, 2.0, -14.8, 20.0]


def test_settings_are_read_from_the_config_keys() -> None:
    """Check notch_settings_from_config reads the five notch keys into NotchSettings.

    Fails if a key is misread or ignored, so a notch saved in a config file would be rebuilt
    with a different value from the one saved.
    """
    config = {
        "CONFIG_NOTCH_ENABLED": 0,
        "CONFIG_NOTCH_ANGLE": 45.0,
        "CONFIG_NOTCH_WIDTH": 3.0,
        "CONFIG_NOTCH_DEPTH": 2.5,
        "CONFIG_NOTCH_HEIGHT": 12.0,
    }
    assert notch_settings_from_config(config) == NotchSettings(
        enabled=False, angle=45.0, width=3.0, depth=2.5, height=12.0
    )


@pytest.mark.parametrize("missing", ["CONFIG_NOTCH_ANGLE", "CONFIG_NOTCH_WIDTH"])
def test_a_config_without_a_notch_key_is_rejected(missing: str) -> None:
    """Check a settings dict missing a notch key raises KeyError rather than guessing a value.

    The live settings always hold every default key, so a missing one means something dropped
    it. Fails if a value is silently invented, which would hide that bug and print a notch
    nobody set.
    """
    config = {
        "CONFIG_NOTCH_ENABLED": 1,
        "CONFIG_NOTCH_ANGLE": 0.0,
        "CONFIG_NOTCH_WIDTH": 2.0,
        "CONFIG_NOTCH_DEPTH": 1.8,
        "CONFIG_NOTCH_HEIGHT": 10.0,
    }
    del config[missing]
    with pytest.raises(KeyError):
        notch_settings_from_config(config)
