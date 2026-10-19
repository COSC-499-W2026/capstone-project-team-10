"""Named needle templates, saved in a JSON file a clinic reuses across plans.

A template records one needle type's channel diameter. The file is a JSON list of
{"name": text, "diameter_mm": number} objects. It is decoded into NeedleTemplate values
here and nowhere else. NeedleTemplateError messages are shown to clinicians on the
Channels tab, so they follow the UI copy rules in AGENTS.md.
"""

import contextlib
import json
import os
from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import Path

from settings.defaults import MINIMUM_CHANNEL_DIAMETER_MM

LIBRARY_FILE_NAME = "needle_templates.json"


type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]


class NeedleTemplateError(ValueError):
    """A needle template, or the library file holding them, cannot be used as written."""


@dataclass(frozen=True)
class NeedleTemplate:
    name: str
    diameter_mm: float


def make_template(name: str, diameter_mm: float) -> NeedleTemplate:
    """Validate a template a clinician typed in, trimming the spaces around its name."""
    trimmed = name.strip()
    if not trimmed:
        raise NeedleTemplateError("A needle template needs a name")
    if not isfinite(diameter_mm) or diameter_mm < MINIMUM_CHANNEL_DIAMETER_MM:
        raise NeedleTemplateError(f"A needle template needs a diameter of at least {MINIMUM_CHANNEL_DIAMETER_MM} mm")
    return NeedleTemplate(trimmed, diameter_mm)


def decode_entry(entry: JsonValue) -> NeedleTemplate:
    """Turn one JSON entry into a template, refusing any entry whose types are not text and a number."""
    match entry:
        case {"name": str(), "diameter_mm": bool()}:
            pass  # a bool is an int in Python, so it must be refused before the number case below
        case {"name": str(name), "diameter_mm": int(diameter) | float(diameter)}:
            return make_template(name, float(diameter))
    raise NeedleTemplateError("an entry is not a name and a diameter")


def load_templates(path: Path) -> tuple[NeedleTemplate, ...]:
    """Read every template in the library, or none if nothing has been saved yet."""
    if not path.exists():
        return ()
    try:
        match json.loads(path.read_text(encoding="utf-8")):
            case list(entries):
                templates = tuple(decode_entry(entry) for entry in entries)
            case _:
                raise NeedleTemplateError("the library is not a list")
    except (OSError, ValueError, OverflowError) as error:
        raise NeedleTemplateError(f"{path.name} could not be read as a needle template library") from error
    if len({template.name for template in templates}) != len(templates):
        raise NeedleTemplateError(f"{path.name} names a needle template twice")
    return templates


def save_template(path: Path, template: NeedleTemplate) -> tuple[NeedleTemplate, ...]:
    """Add a template, replacing any with the same name, and write the library back."""
    templates = tuple(saved for saved in load_templates(path) if saved.name != template.name) + (template,)
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps([asdict(saved) for saved in templates], indent=2), encoding="utf-8")
        os.replace(temporary, path)
    except OSError as error:
        with contextlib.suppress(OSError):
            temporary.unlink(missing_ok=True)
        raise NeedleTemplateError(f"{path.name} could not be saved") from error
    return templates
