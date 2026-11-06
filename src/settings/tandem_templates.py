"""Named tandem templates, saved in a JSON file a clinic reuses across plans.

A template records the Tandem tab's eight Generate settings, lengths in mm and angles in
degrees, rotation included. The file is {"version": 1, "templates": [...]}, decoded into
TandemTemplate values here and nowhere else. Like settings.cylinder_templates, whose decoders and
safe save it shares, this module imports nothing from classes or windows. TandemTemplateError
messages are shown to clinicians on the Tandem tab, so they follow the UI copy rules in AGENTS.md.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from settings.cylinder_templates import JsonValue, Range, decode_number, decode_time, name_key, write_atomically

LIBRARY_FILE_NAME = "tandem_templates.json"
LIBRARY_VERSION = 1


class TandemTemplateError(ValueError):
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


def load_templates(path: Path) -> tuple[TandemTemplate, ...]:
    """Read every template in the library, or none if nothing has been saved yet."""
    if not path.exists():
        return ()
    try:
        match json.loads(path.read_text(encoding="utf-8")):
            case {"version": int(version), "templates": list(entries)} if version == LIBRARY_VERSION:
                templates = tuple(decode_template(entry) for entry in entries)
            case _:
                raise TandemTemplateError(f"it is not a version {LIBRARY_VERSION} tandem template library")
        if len({template.template_id for template in templates}) != len(templates):
            raise TandemTemplateError("two templates share an ID")
        if len({name_key(template.name) for template in templates}) != len(templates):
            raise TandemTemplateError("two templates share a name")
    except (OSError, ValueError, OverflowError) as error:
        raise TandemTemplateError(f"{path.name} could not be read. {error}") from error
    return templates


def write_templates(path: Path, templates: tuple[TandemTemplate, ...]) -> None:
    """Write the library through write_atomically, so a failed save keeps the old file."""
    library = {"version": LIBRARY_VERSION, "templates": [encode_template(template) for template in templates]}
    try:
        write_atomically(path, json.dumps(library, indent=2))
    except OSError as error:
        raise TandemTemplateError(f"{path.name} could not be saved") from error


def name_taken(templates: tuple[TandemTemplate, ...], name: str, template_id: str) -> bool:
    """Whether a template other than template_id already uses this name, in any case."""
    return any(name_key(saved.name) == name_key(name) and saved.template_id != template_id for saved in templates)


def add_template(path: Path, template: TandemTemplate) -> tuple[TandemTemplate, ...]:
    """Add a new template and write the library back, refusing a name already used in any case."""
    templates = load_templates(path)
    if name_taken(templates, template.name, template.template_id):
        raise TandemTemplateError(f"A tandem template named {template.name} already exists. Use Update to change it")
    if any(saved.template_id == template.template_id for saved in templates):
        raise TandemTemplateError("A tandem template with this ID already exists")
    templates += (template,)
    write_templates(path, templates)
    return templates
