from collections.abc import Mapping
from dataclasses import dataclass

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Pnt, gp
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Extend.ShapeFactory import rotate_shape

# how far the notch box starts inside the cylinder wall, so the two fuse into one solid
WALL_OVERLAP = 0.2


@dataclass(frozen=True)
class NotchSettings:
    """
    The orientation notch as the clinician sets it, lengths in mm.
    angle is in degrees clockwise from Anterior as the reference sheet draws it,
    depth is how far the notch stands out of the wall, height is how far it runs up from the base.
    """
    enabled: bool = True
    angle: float = 0.0
    width: float = 2.0
    depth: float = 1.8
    height: float = 10.0


def notch_settings_from_config(config: Mapping[str, float]) -> NotchSettings:
    """Read the five notch settings from a config dict. A missing key raises KeyError."""
    return NotchSettings(
        enabled=bool(config["CONFIG_NOTCH_ENABLED"]),
        angle=float(config["CONFIG_NOTCH_ANGLE"]),
        width=float(config["CONFIG_NOTCH_WIDTH"]),
        depth=float(config["CONFIG_NOTCH_DEPTH"]),
        height=float(config["CONFIG_NOTCH_HEIGHT"]),
    )


class CylinderNotch:
    """
    A small box at Z=0 standing out of the cylinder wall to mark its orientation
    """

    def shape(self) -> TopoDS_Shape:
        start_x = self.radius - WALL_OVERLAP
        point = gp_Pnt(start_x, -self.width/2, 0)
        notch = BRepPrimAPI_MakeBox(point, self.height, self.width, self.length).Shape()

        # rotate the notch along 0, 0, 1
        return rotate_shape(shape=notch, axis=gp.OZ(), angle=self.rotation, unite="deg")

    def __init__(self, diameter: float, settings: NotchSettings, length: float):
        self.width = settings.width
        self.length = length  # along the cylinder axis
        self.height = settings.depth + WALL_OVERLAP  # radial size of the box

        # the sheet is drawn looking up from the base with y negated, so its clockwise angle
        # from Anterior (the model's -y side) is the model's angle plus 90 degrees
        self.rotation = (settings.angle - 90.0) % 360.0
        self.radius = diameter / 2
