"""Pure rows for the Import-tab structure list."""

from __future__ import annotations

from dataclasses import dataclass

from classes.dicom.structures import Structure


@dataclass(frozen=True)
class StructureListRow:
    """One read-only list entry: display label, DICOM RGB colour, category text."""

    label: str
    color: tuple[int, int, int]
    category: str


def structure_list_rows(
    structures: tuple[Structure, ...] | None,
) -> tuple[StructureListRow, ...]:
    """Build Import-tab rows from decoded structures.

    Duplicate names get an ROI suffix so two entries stay distinguishable.
    None or an empty tuple yields no rows.
    """
    if not structures:
        return ()
    name_counts: dict[str, int] = {}
    for structure in structures:
        name_counts[structure.name] = name_counts.get(structure.name, 0) + 1
    rows: list[StructureListRow] = []
    for structure in structures:
        label = structure.name
        if name_counts[structure.name] > 1:
            label = f"{structure.name} (ROI {structure.roi_number})"
        rows.append(
            StructureListRow(label, structure.color, structure.category.value)
        )
    return tuple(rows)
