"""Named tandem templates, saved in a JSON file a clinic reuses across plans.

A template records the Tandem tab's eight Generate settings, lengths in mm and angles in
degrees, rotation included. The file is {"version": 1, "templates": [...]}, decoded into
TandemTemplate values here and nowhere else. Loading, saving, adding, updating and deleting are
the shared rules in settings.template_library, which this module configures through LIBRARY,
so what stays here is only what makes a tandem template different: its settings, their limits,
and how one entry is decoded and encoded. Like that module, this one imports nothing from
classes or windows. TandemTemplateError messages are shown to clinicians on the Tandem tab, so
they follow the UI copy rules in AGENTS.md.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from settings.template_library import JsonValue, Range, TemplateLibrary, TemplateLibraryError, decode_number, decode_time

LIBRARY_FILE_NAME = "tandem_templates.json"
LIBRARY_VERSION = 1


class TandemTemplateError(TemplateLibraryError):
    """A tandem template, or the library file holding them, cannot be used as written."""


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
    LIBRARY.check_ranges(asdict(design), RANGES)


def make_template(template_id: str, name: str, note: str, design: TandemDesign,
                  created: datetime, modified: datetime) -> TandemTemplate:
    """Validate a template, trimming the spaces around its name and note."""
    trimmed = LIBRARY.validated_name(template_id, name, created, modified)
    check_design(design)
    return TandemTemplate(template_id, trimmed, note.strip(), created, modified, design)


def decode_template(entry: JsonValue) -> TandemTemplate:
    """Turn one JSON entry into a template, refusing any entry with a missing or mistyped value."""
    match entry:
        case {"id": str(template_id), "name": str(name), "note": str(note),
              "created": str(created), "modified": str(modified)}:
            design = TandemDesign(
                height_mm=decode_number(entry.get("height_mm"), "height_mm"),
                channel_diameter_mm=decode_number(entry.get("channel_diameter_mm"), "channel_diameter_mm"),
                stopper_diameter_mm=decode_number(entry.get("stopper_diameter_mm"), "stopper_diameter_mm"),
                bend_angle_deg=decode_number(entry.get("bend_angle_deg"), "bend_angle_deg"),
                bend_radius_mm=decode_number(entry.get("bend_radius_mm"), "bend_radius_mm"),
                threading_depth_mm=decode_number(entry.get("threading_depth_mm"), "threading_depth_mm"),
                threading_diameter_mm=decode_number(entry.get("threading_diameter_mm"), "threading_diameter_mm"),
                rotation_deg=decode_number(entry.get("rotation_deg"), "rotation_deg"),
            )
            return make_template(template_id, name, note, design, decode_time(created), decode_time(modified))
    raise TandemTemplateError("an entry is not a tandem template")


def encode_template(template: TandemTemplate) -> dict[str, JsonValue]:
    return {"id": template.template_id, "name": template.name, "note": template.note,
            "created": template.created.isoformat(), "modified": template.modified.isoformat(),
            **asdict(template.design)}


LIBRARY = TemplateLibrary("tandem", TandemTemplateError, LIBRARY_VERSION, decode_template, encode_template)

load_templates = LIBRARY.load
write_templates = LIBRARY.write
position = LIBRARY.position
add_template = LIBRARY.add
delete_template = LIBRARY.delete


def update_template(path: Path, template_id: str, name: str, note: str,
                    design: TandemDesign, now: datetime) -> tuple[TandemTemplate, ...]:
    """Replace a template's name, note and design, keeping its ID, created date and place in the list."""
    def revise(saved: TandemTemplate) -> TandemTemplate:
        return make_template(template_id, name, note, design, saved.created, now)

    return LIBRARY.update(path, template_id, revise)
