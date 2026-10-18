"""Named needle templates, saved in a JSON file a clinic reuses across plans.

A template records one needle type's channel diameter. The file is a JSON list of
{"name": text, "diameter_mm": number} objects. It is decoded into NeedleTemplate values
here and nowhere else. NeedleTemplateError messages are shown to clinicians on the
Channels tab, so they follow the UI copy rules in AGENTS.md.
"""

import json
from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import Path

from settings.defaults import MINIMUM_CHANNEL_DIAMETER_MM

LIBRARY_FILE_NAME = "needle_templates.json"


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


def load_templates(path: Path) -> tuple[NeedleTemplate, ...]:
    """Read every template in the library, or none if nothing has been saved yet."""
    if not path.exists():
        return ()
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
        templates = tuple(make_template(str(entry["name"]), float(entry["diameter_mm"])) for entry in entries)
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise NeedleTemplateError(f"{path.name} could not be read as a needle template library") from error
    if len({template.name for template in templates}) != len(templates):
        raise NeedleTemplateError(f"{path.name} names a needle template twice")
    return templates


def save_template(path: Path, template: NeedleTemplate) -> tuple[NeedleTemplate, ...]:
    """Add a template, replacing any with the same name, and write the library back."""
    templates = tuple(saved for saved in load_templates(path) if saved.name != template.name) + (template,)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([asdict(saved) for saved in templates], indent=2), encoding="utf-8")
    except OSError as error:
        raise NeedleTemplateError(f"{path.name} could not be saved") from error
    return templates
