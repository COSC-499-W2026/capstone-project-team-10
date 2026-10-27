"""Pure rows for the Import inventory and the Structures-tab anatomy list."""

from __future__ import annotations

from dataclasses import dataclass

from classes.dicom.structures import Structure, StructureType


@dataclass(frozen=True)
class StructureListRow:
    """One read-only list entry: display label, DICOM RGB colour, category text."""

    label: str
    color: tuple[int, int, int]
    category: str


def _label_for(structure: Structure, name_counts: dict[str, int], used: set[str]) -> str:
    """Pick a list label that does not collide with one already shown."""
    label = structure.name
    if name_counts[structure.name] > 1:
        label = f"{structure.name} (ROI {structure.roi_number})"
    if label in used:
        label = f"{structure.name} (ROI {structure.roi_number})"
    if label in used:
        label = f"{structure.name} (ROI {structure.roi_number}) #{structure.roi_number}"
    return label


def anatomy_structures(
    structures: tuple[Structure, ...] | None,
) -> tuple[Structure, ...]:
    """Keep organs and tumours for the Structures tab.

    Needles, body outlines, markers and other ROIs stay in DicomData and on
    the Import inventory. None or an empty tuple yields no rows.
    """
    if not structures:
        return ()
    return tuple(
        structure
        for structure in structures
        if structure.category in (StructureType.ORGAN, StructureType.TUMOUR)
    )


def structure_list_rows(
    structures: tuple[Structure, ...] | None,
) -> tuple[StructureListRow, ...]:
    """Build Import-tab rows from decoded structures.

    Duplicate names get an ROI suffix so two entries stay distinguishable.
    If that suffix would still match another row's label, a further unique
    form is used. None or an empty tuple yields no rows.
    """
    if not structures:
        return ()
    name_counts: dict[str, int] = {}
    for structure in structures:
        name_counts[structure.name] = name_counts.get(structure.name, 0) + 1
    used: set[str] = set()
    rows: list[StructureListRow] = []
    for structure in structures:
        label = _label_for(structure, name_counts, used)
        used.add(label)
        rows.append(
            StructureListRow(label, structure.color, structure.category.value)
        )
    return tuple(rows)
