"""Named cylinder templates, saved in a JSON file a clinic reuses across patients.

A template records the Cylinder tab's 11 settings, lengths in mm. The file is
{"version": 1, "templates": [...]}, decoded into CylinderTemplate values here and nowhere else.
This module imports nothing from classes or windows: classes.mesh.cylinder cannot be imported
before the app exists, so the Cylinder tab converts a CylinderDesign to TipShape and
NotchSettings itself. CylinderTemplateError messages are shown to clinicians on the Cylinder
tab, so they follow the UI copy rules in AGENTS.md.
"""

import contextlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

LIBRARY_FILE_NAME = "cylinder_templates.json"
LIBRARY_VERSION = 1


type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]


class CylinderTemplateError(ValueError):
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


def decode_number(value: JsonValue, key: str) -> float:
    """Read one JSON number, refusing a boolean, which Python would otherwise treat as 0 or 1."""
    match value:
        case bool():
            pass
        case int() | float():
            return float(value)
    raise CylinderTemplateError(f"{key} is not a number")


def decode_flag(value: JsonValue, key: str) -> bool:
    match value:
        case bool(flag):
            return flag
    raise CylinderTemplateError(f"{key} is not true or false")


def decode_time(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise CylinderTemplateError(f"{value} is not a date") from error


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


def name_key(name: str) -> str:
    """The form two names are compared in, so "Standard" and "STANDARD" count as one name."""
    return name.casefold()


def load_templates(path: Path) -> tuple[CylinderTemplate, ...]:
    """Read every template in the library, or none if nothing has been saved yet."""
    if not path.exists():
        return ()
    try:
        match json.loads(path.read_text(encoding="utf-8")):
            case {"version": int(version), "templates": list(entries)} if version == LIBRARY_VERSION:
                templates = tuple(decode_template(entry) for entry in entries)
            case _:
                raise CylinderTemplateError(f"it is not a version {LIBRARY_VERSION} cylinder template library")
        if len({template.template_id for template in templates}) != len(templates):
            raise CylinderTemplateError("two templates share an ID")
        if len({name_key(template.name) for template in templates}) != len(templates):
            raise CylinderTemplateError("two templates share a name")
    except (OSError, ValueError, OverflowError) as error:
        raise CylinderTemplateError(f"{path.name} could not be read. {error}") from error
    return templates


def write_templates(path: Path, templates: tuple[CylinderTemplate, ...]) -> None:
    """Write the library to a .tmp file beside it and swap that in, so a failed save keeps the old file."""
    library = {"version": LIBRARY_VERSION, "templates": [encode_template(template) for template in templates]}
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(library, indent=2), encoding="utf-8")
        os.replace(temporary, path)
    except OSError as error:
        with contextlib.suppress(OSError):
            temporary.unlink(missing_ok=True)
        raise CylinderTemplateError(f"{path.name} could not be saved") from error


def name_taken(templates: tuple[CylinderTemplate, ...], name: str, template_id: str) -> bool:
    """Whether a template other than template_id already uses this name, in any case."""
    return any(name_key(saved.name) == name_key(name) and saved.template_id != template_id for saved in templates)


def position(templates: tuple[CylinderTemplate, ...], template_id: str) -> int:
    """Where the template with this ID sits in the library, or an error if it has gone."""
    for index, saved in enumerate(templates):
        if saved.template_id == template_id:
            return index
    raise CylinderTemplateError("That cylinder template no longer exists")


def add_template(path: Path, template: CylinderTemplate) -> tuple[CylinderTemplate, ...]:
    """Add a new template and write the library back, refusing a name already used in any case."""
    templates = load_templates(path)
    if name_taken(templates, template.name, template.template_id):
        raise CylinderTemplateError(f"A cylinder template named {template.name} already exists. Use Update to change it")
    if any(saved.template_id == template.template_id for saved in templates):
        raise CylinderTemplateError("A cylinder template with this ID already exists")
    templates += (template,)
    write_templates(path, templates)
    return templates


def update_template(path: Path, template_id: str, name: str, note: str,
                    design: CylinderDesign, now: datetime) -> tuple[CylinderTemplate, ...]:
    """Replace a template's name, note and design, keeping its ID, created date and place in the list."""
    templates = load_templates(path)
    index = position(templates, template_id)
    updated = make_template(template_id, name, note, design, templates[index].created, now)
    if name_taken(templates, updated.name, template_id):
        raise CylinderTemplateError(f"A cylinder template named {updated.name} already exists")
    templates = templates[:index] + (updated,) + templates[index + 1:]
    write_templates(path, templates)
    return templates


def delete_template(path: Path, template_id: str) -> tuple[CylinderTemplate, ...]:
    """Remove one template and write the library back."""
    templates = load_templates(path)
    index = position(templates, template_id)
    templates = templates[:index] + templates[index + 1:]
    write_templates(path, templates)
    return templates
