"""Named tandem templates, which a clinic reuses across plans.

A template records the Tandem tab's eight Generate settings, lengths in mm and angles in
degrees, rotation included. Like settings.cylinder_templates, whose Range it shares, this module
imports nothing from classes or windows. TandemTemplateError messages are shown to clinicians on
the Tandem tab, so they follow the UI copy rules in AGENTS.md.
"""

from dataclasses import asdict, dataclass
from datetime import datetime

from settings.cylinder_templates import Range


class TandemTemplateError(ValueError):
    """A tandem template cannot be used as written."""


@dataclass(frozen=True)
class TandemDesign:
    """The Generate sub-tab's settings, lengths in mm and angles in degrees."""
    height_mm: float
    channel_diameter_mm: float
    stopper_diameter_mm: float
    bend_angle_deg: float
    bend_radius_mm: float
    threading_depth_mm: float
    threading_diameter_mm: float
    rotation_deg: float


@dataclass(frozen=True)
class TandemTemplate:
    template_id: str
    name: str
    note: str
    created: datetime
    modified: datetime
    design: TandemDesign


# The Generate sub-tab's spin box limits, from tandem_view.ui. A box the .ui gives no maximum
# keeps Qt's default of 99.99, and one given no minimum keeps 0.
RANGES = {
    "height_mm": Range("Tandem Height", 10.0, 500.0, " mm"),
    "channel_diameter_mm": Range("Channel Diameter", 0.5, 99.99, " mm"),
    "stopper_diameter_mm": Range("Stopper Diameter", 0.5, 99.99, " mm"),
    "bend_angle_deg": Range("Bend Angle", 0.0, 99.99, "°"),
    "bend_radius_mm": Range("Bend Radius", 10.0, 1000.0, " mm"),
    "threading_depth_mm": Range("Threading Depth", 0.0, 350.0, " mm"),
    "threading_diameter_mm": Range("Threading Diameter", 0.0, 350.0, " mm"),
    "rotation_deg": Range("Rotation", -360.0, 360.0, "°"),
}


def check_design(design: TandemDesign) -> None:
    """Refuse a value the Generate sub-tab could not show, NaN and infinity included."""
    for key, value in asdict(design).items():
        allowed = RANGES[key]
        if not allowed.minimum <= value <= allowed.maximum:
            raise TandemTemplateError(
                f"{allowed.label} must be from {allowed.minimum:g} to {allowed.maximum:g}{allowed.unit}")


def make_template(template_id: str, name: str, note: str, design: TandemDesign,
                  created: datetime, modified: datetime) -> TandemTemplate:
    """Validate a template, trimming the spaces around its name and note."""
    trimmed = name.strip()
    if not trimmed:
        raise TandemTemplateError("A tandem template needs a name")
    if not template_id:
        raise TandemTemplateError("A tandem template needs an ID")
    if created.tzinfo is None or modified.tzinfo is None:
        raise TandemTemplateError("A tandem template's dates need a time zone")
    if modified < created:
        raise TandemTemplateError("A tandem template cannot be modified before it was created")
    check_design(design)
    return TandemTemplate(template_id, trimmed, note.strip(), created, modified, design)
