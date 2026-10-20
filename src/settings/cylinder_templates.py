"""Named cylinder templates a clinic reuses across patients.

A template records the Cylinder tab's 11 settings, lengths in mm. This module imports nothing
from classes or windows: classes.mesh.cylinder cannot be imported before the app exists, so the
Cylinder tab converts a CylinderDesign to TipShape and NotchSettings itself.
CylinderTemplateError messages are shown to clinicians on the Cylinder tab, so they follow the
UI copy rules in AGENTS.md.
"""

from dataclasses import dataclass
from datetime import datetime


class CylinderTemplateError(ValueError):
    """A cylinder template cannot be used as written."""


@dataclass(frozen=True)
class CylinderDesign:
    """The Cylinder tab's settings, lengths in mm and the notch angle in degrees."""
    diameter_mm: float
    length_mm: float
    collar_enabled: bool
    collar_thickness_mm: float
    collar_height_mm: float
    notch_enabled: bool
    notch_angle_deg: float
    notch_width_mm: float
    notch_depth_mm: float
    notch_height_mm: float
    flat_tip: bool


@dataclass(frozen=True)
class CylinderTemplate:
    template_id: str
    name: str
    note: str
    created: datetime
    modified: datetime
    design: CylinderDesign


@dataclass(frozen=True)
class Range:
    """The values a Cylinder tab spin box allows, for the message that names the setting."""
    label: str
    minimum: float
    maximum: float
    unit: str


# The Cylinder tab's spin box limits in mm, from cylinder_view.ui. The diameter box has two
# decimals and no minimum set, so 0.01 mm is the smallest diameter that builds a cylinder.
RANGES = {
    "diameter_mm": Range("Cylinder Diameter", 0.01, 99.99, " mm"),
    "length_mm": Range("Cylinder Length", 60.0, 300.0, " mm"),
    "collar_thickness_mm": Range("Collar Thickness", 0.0, 99.0, " mm"),
    "collar_height_mm": Range("Collar Height", 0.0, 99.0, " mm"),
    "notch_angle_deg": Range("Notch Angle", 0.0, 359.9, "°"),
    "notch_width_mm": Range("Notch Width", 0.5, 10.0, " mm"),
    "notch_depth_mm": Range("Notch Depth", 0.5, 5.0, " mm"),
    "notch_height_mm": Range("Notch Height", 1.0, 60.0, " mm"),
}


def ranged_values(design: CylinderDesign) -> dict[str, float]:
    """The design's numbers, keyed as in RANGES."""
    return {
        "diameter_mm": design.diameter_mm,
        "length_mm": design.length_mm,
        "collar_thickness_mm": design.collar_thickness_mm,
        "collar_height_mm": design.collar_height_mm,
        "notch_angle_deg": design.notch_angle_deg,
        "notch_width_mm": design.notch_width_mm,
        "notch_depth_mm": design.notch_depth_mm,
        "notch_height_mm": design.notch_height_mm,
    }


def check_design(design: CylinderDesign) -> None:
    """Refuse a value the Cylinder tab could not show, NaN and infinity included."""
    for key, value in ranged_values(design).items():
        allowed = RANGES[key]
        if not allowed.minimum <= value <= allowed.maximum:
            raise CylinderTemplateError(
                f"{allowed.label} must be from {allowed.minimum:g} to {allowed.maximum:g}{allowed.unit}")


def make_template(template_id: str, name: str, note: str, design: CylinderDesign,
                  created: datetime, modified: datetime) -> CylinderTemplate:
    """Validate a template, trimming the spaces around its name and note."""
    trimmed = name.strip()
    if not trimmed:
        raise CylinderTemplateError("A cylinder template needs a name")
    if not template_id:
        raise CylinderTemplateError("A cylinder template needs an ID")
    if created.tzinfo is None or modified.tzinfo is None:
        raise CylinderTemplateError("A cylinder template's dates need a time zone")
    if modified < created:
        raise CylinderTemplateError("A cylinder template cannot be modified before it was created")
    check_design(design)
    return CylinderTemplate(template_id, trimmed, note.strip(), created, modified, design)
