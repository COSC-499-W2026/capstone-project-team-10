"""Named cylinder templates, saved in a JSON file a clinic reuses across patients.

A template records the Cylinder tab's 11 settings, lengths in mm. The file is
{"version": 1, "templates": [...]}, decoded into CylinderTemplate values here and nowhere else.
Loading, saving, adding, updating and deleting are the shared rules in settings.template_library,
which this module configures through LIBRARY, so what stays here is only what makes a cylinder
template different: its settings, their limits, and how one entry is decoded and encoded.
This module imports nothing from classes or windows: classes.mesh.cylinder cannot be imported
before the app exists, so the Cylinder tab converts a CylinderDesign to TipShape and
NotchSettings itself. CylinderTemplateError messages are shown to clinicians on the Cylinder
tab, so they follow the UI copy rules in AGENTS.md.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from settings.template_library import (
    JsonValue, Range, TemplateLibrary, TemplateLibraryError, decode_flag, decode_number, decode_time,
)

LIBRARY_FILE_NAME = "cylinder_templates.json"
LIBRARY_VERSION = 1


class CylinderTemplateError(TemplateLibraryError):
    """A cylinder template, or the library file holding them, cannot be used as written."""


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
    """The design's numbers, keyed as in RANGES and in the JSON file."""
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
    LIBRARY.check_ranges(ranged_values(design), RANGES)


def make_template(template_id: str, name: str, note: str, design: CylinderDesign,
                  created: datetime, modified: datetime) -> CylinderTemplate:
    """Validate a template, trimming the spaces around its name and note."""
    trimmed = LIBRARY.validated_name(template_id, name, created, modified)
    check_design(design)
    return CylinderTemplate(template_id, trimmed, note.strip(), created, modified, design)


def decode_template(entry: JsonValue) -> CylinderTemplate:
    """Turn one JSON entry into a template, refusing any entry with a missing or mistyped value."""
    match entry:
        case {"id": str(template_id), "name": str(name), "note": str(note),
              "created": str(created), "modified": str(modified)}:
            design = CylinderDesign(
                diameter_mm=decode_number(entry.get("diameter_mm"), "diameter_mm"),
                length_mm=decode_number(entry.get("length_mm"), "length_mm"),
                collar_enabled=decode_flag(entry.get("collar_enabled"), "collar_enabled"),
                collar_thickness_mm=decode_number(entry.get("collar_thickness_mm"), "collar_thickness_mm"),
                collar_height_mm=decode_number(entry.get("collar_height_mm"), "collar_height_mm"),
                notch_enabled=decode_flag(entry.get("notch_enabled"), "notch_enabled"),
                notch_angle_deg=decode_number(entry.get("notch_angle_deg"), "notch_angle_deg"),
                notch_width_mm=decode_number(entry.get("notch_width_mm"), "notch_width_mm"),
                notch_depth_mm=decode_number(entry.get("notch_depth_mm"), "notch_depth_mm"),
                notch_height_mm=decode_number(entry.get("notch_height_mm"), "notch_height_mm"),
                flat_tip=decode_flag(entry.get("flat_tip"), "flat_tip"),
            )
            return make_template(template_id, name, note, design, decode_time(created), decode_time(modified))
    raise CylinderTemplateError("an entry is not a cylinder template")


def encode_template(template: CylinderTemplate) -> dict[str, JsonValue]:
    return {"id": template.template_id, "name": template.name, "note": template.note,
            "created": template.created.isoformat(), "modified": template.modified.isoformat(),
            **asdict(template.design)}


LIBRARY = TemplateLibrary("cylinder", CylinderTemplateError, LIBRARY_VERSION, decode_template, encode_template)

load_templates = LIBRARY.load
write_templates = LIBRARY.write
position = LIBRARY.position
add_template = LIBRARY.add
delete_template = LIBRARY.delete


def update_template(path: Path, template_id: str, name: str, note: str,
                    design: CylinderDesign, now: datetime) -> tuple[CylinderTemplate, ...]:
    """Replace a template's name, note and design, keeping its ID, created date and place in the list."""
    def revise(saved: CylinderTemplate) -> CylinderTemplate:
        return make_template(template_id, name, note, design, saved.created, now)

    return LIBRARY.update(path, template_id, revise)
