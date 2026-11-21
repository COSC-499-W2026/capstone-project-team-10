"""The rules every named template library shares, so a kind of template only says what makes it different.

Cylinder and tandem templates are saved the same way: a JSON file {"version": 1, "templates": [...]},
read whole, checked, and written back through a temporary file. A kind builds one TemplateLibrary
from its noun, its error class, and how to decode and encode one entry, and gets load, write, add,
update and delete from it. This module imports nothing from classes or windows, because
classes.mesh.cylinder cannot be imported before the app exists. Messages are shown to clinicians,
so they follow the UI copy rules in AGENTS.md.
"""

import contextlib
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]


class TemplateLibraryError(ValueError):
    """A template, or the library file holding them, cannot be used as written. Each kind subclasses it."""


@dataclass(frozen=True)
class Range:
    """The values a tab's spin box allows, for the message that names the setting."""
    label: str
    minimum: float
    maximum: float
    unit: str


class LibraryEntry(Protocol):
    """What the library needs from a template of any kind, which is an ID and a name."""

    @property
    def template_id(self) -> str: ...

    @property
    def name(self) -> str: ...


def decode_number(value: JsonValue, key: str) -> float:
    """Read one JSON number, refusing a boolean, which Python would otherwise treat as 0 or 1."""
    match value:
        case bool():
            pass
        case int() | float():
            return float(value)
    raise TemplateLibraryError(f"{key} is not a number")


def decode_flag(value: JsonValue, key: str) -> bool:
    """Read one JSON true or false, refusing a number, which Python would otherwise treat as a flag."""
    match value:
        case bool(flag):
            return flag
    raise TemplateLibraryError(f"{key} is not true or false")


def decode_time(value: str) -> datetime:
    """Read one ISO date and time."""
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise TemplateLibraryError(f"{value} is not a date") from error


def name_key(name: str) -> str:
    """The form two names are compared in, so "Standard" and "STANDARD" count as one name."""
    return name.casefold()


def name_taken[T: LibraryEntry](templates: tuple[T, ...], name: str, template_id: str) -> bool:
    """Whether a template other than template_id already uses this name, in any case."""
    return any(name_key(saved.name) == name_key(name) and saved.template_id != template_id for saved in templates)


def write_atomically(path: Path, text: str) -> None:
    """Write text to a .tmp file beside path and swap that in, so a failed write keeps the old file.

    Raises the OSError, after removing the .tmp file, for the caller to report.
    """
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)
    except OSError:
        with contextlib.suppress(OSError):
            temporary.unlink(missing_ok=True)
        raise


@dataclass(frozen=True)
class TemplateLibrary[T: LibraryEntry]:
    """How to keep one kind of template in a JSON file. The kind supplies what differs, this class the rules."""
    noun: str
    error: type[TemplateLibraryError]
    version: int
    decode: Callable[[JsonValue], T]
    encode: Callable[[T], dict[str, JsonValue]]

    def validated_name(self, template_id: str, name: str, created: datetime, modified: datetime) -> str:
        """Refuse a template with no name or ID, or dates that cannot be compared, and return the trimmed name."""
        trimmed = name.strip()
        if not trimmed:
            raise self.error(f"A {self.noun} template needs a name")
        if not template_id:
            raise self.error(f"A {self.noun} template needs an ID")
        if created.tzinfo is None or modified.tzinfo is None:
            raise self.error(f"A {self.noun} template's dates need a time zone")
        if modified < created:
            raise self.error(f"A {self.noun} template cannot be modified before it was created")
        return trimmed

    def check_ranges(self, values: dict[str, float], ranges: dict[str, Range]) -> None:
        """Refuse a value outside its tab's limits, NaN and infinity included."""
        for key, value in values.items():
            allowed = ranges[key]
            if not allowed.minimum <= value <= allowed.maximum:
                raise self.error(
                    f"{allowed.label} must be from {allowed.minimum:g} to {allowed.maximum:g}{allowed.unit}")

    def load(self, path: Path) -> tuple[T, ...]:
        """Read every template in the library, or none if nothing has been saved yet."""
        if not path.exists():
            return ()
        try:
            match json.loads(path.read_text(encoding="utf-8")):
                case {"version": int(version), "templates": list(entries)} if version == self.version:
                    templates = tuple(self.decode(entry) for entry in entries)
                case _:
                    raise self.error(f"it is not a version {self.version} {self.noun} template library")
            if len({template.template_id for template in templates}) != len(templates):
                raise self.error("two templates share an ID")
            if len({name_key(template.name) for template in templates}) != len(templates):
                raise self.error("two templates share a name")
        except (OSError, ValueError, OverflowError) as error:
            raise self.error(f"{path.name} could not be read. {error}") from error
        return templates

    def write(self, path: Path, templates: tuple[T, ...]) -> None:
        """Write the library through write_atomically, so a failed save keeps the old file."""
        library = {"version": self.version, "templates": [self.encode(template) for template in templates]}
        try:
            write_atomically(path, json.dumps(library, indent=2))
        except OSError as error:
            raise self.error(f"{path.name} could not be saved") from error

    def position(self, templates: tuple[T, ...], template_id: str) -> int:
        """Where the template with this ID sits in the library, or an error if it has gone."""
        for index, saved in enumerate(templates):
            if saved.template_id == template_id:
                return index
        raise self.error(f"That {self.noun} template no longer exists")

    def add(self, path: Path, template: T) -> tuple[T, ...]:
        """Add a new template and write the library back, refusing a name already used in any case."""
        templates = self.load(path)
        if name_taken(templates, template.name, template.template_id):
            raise self.error(f"A {self.noun} template named {template.name} already exists. Use Update to change it")
        if any(saved.template_id == template.template_id for saved in templates):
            raise self.error(f"A {self.noun} template with this ID already exists")
        templates += (template,)
        self.write(path, templates)
        return templates

    def update(self, path: Path, template_id: str, revise: Callable[[T], T]) -> tuple[T, ...]:
        """Replace one template with revise(saved), keeping its place in the list, and write the library back."""
        templates = self.load(path)
        index = self.position(templates, template_id)
        updated = revise(templates[index])
        if name_taken(templates, updated.name, template_id):
            raise self.error(f"A {self.noun} template named {updated.name} already exists")
        templates = templates[:index] + (updated,) + templates[index + 1:]
        self.write(path, templates)
        return templates

    def delete(self, path: Path, template_id: str) -> tuple[T, ...]:
        """Remove one template and write the library back."""
        templates = self.load(path)
        index = self.position(templates, template_id)
        templates = templates[:index] + templates[index + 1:]
        self.write(path, templates)
        return templates
