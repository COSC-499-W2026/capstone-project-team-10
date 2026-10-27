"""Tests for Import-tab structure list rows built from decoded Structures."""

from classes.dicom.structure_list import (
    StructureListRow,
    anatomy_structures,
    structure_list_rows,
)
from classes.dicom.structures import Structure, StructureType


def _structure(
    roi_number: int,
    name: str,
    category: StructureType,
    color: tuple[int, int, int] = (10, 20, 30),
) -> Structure:
    """Helper: build a Structure with no contours for list-row tests."""
    return Structure(
        roi_number,
        name,
        "1.2.3",
        color,
        None,
        category,
        (),
    )


def test_structure_list_rows_include_name_colour_and_category() -> None:
    """Check that each row carries the structure's name, RGB colour and category.

    Fails if a row drops the name, remaps the colour, or shows a different
    category string than StructureType.value. The Import list has no other
    source for those three fields, so a wrong row would mislead the clinician
    about which anatomy is in the plan.
    """
    rows = structure_list_rows(
        (
            _structure(1, "Bladder", StructureType.ORGAN, (1, 2, 3)),
            _structure(2, "GTV", StructureType.TUMOUR, (200, 0, 0)),
        )
    )

    assert rows == (
        StructureListRow("Bladder", (1, 2, 3), "organ"),
        StructureListRow("GTV", (200, 0, 0), "tumour"),
    )


def test_duplicate_names_include_roi_number_in_the_label() -> None:
    """Check that two structures with the same name stay distinguishable by ROI.

    Fails if both labels are identical, or if a unique name also gets an ROI
    suffix. Duplicate ROI names are common across plans; without the number the
    list cannot tell the clinician which entry is which (FR-SV-02).
    """
    rows = structure_list_rows(
        (
            _structure(7, "Node", StructureType.OTHER),
            _structure(8, "Node", StructureType.ORGAN),
            _structure(9, "Unique", StructureType.OTHER),
        )
    )

    assert rows[0].label == "Node (ROI 7)"
    assert rows[1].label == "Node (ROI 8)"
    assert rows[2].label == "Unique"


def test_structure_list_rows_for_missing_structures_is_empty() -> None:
    """Check that None or an empty tuple yields no list rows.

    Fails if a previous plan's rows would be invented from None, or if an empty
    decode still produces a placeholder. Import must clear the list when there
    are no structures so anatomy from the last plan cannot linger.
    """
    assert structure_list_rows(None) == ()
    assert structure_list_rows(()) == ()


def test_roi_suffix_avoids_colliding_with_an_existing_label() -> None:
    """Check that a plain name which already matches another label still gets a unique row.

    One structure is literally named `Node (ROI 7)`. Two others are both named `Node`.
    Fails if the first duplicate keeps `Node (ROI 7)` and shares a label with the
    named structure. The Import list must never show two identical labels (FR-SV-02).
    """
    rows = structure_list_rows(
        (
            _structure(1, "Node (ROI 7)", StructureType.OTHER),
            _structure(7, "Node", StructureType.ORGAN),
            _structure(8, "Node", StructureType.OTHER),
        )
    )

    labels = [row.label for row in rows]
    assert labels[0] == "Node (ROI 7)"
    assert labels[1] != labels[0]
    assert labels[2] != labels[0]
    assert labels[1] != labels[2]
    assert len(set(labels)) == 3


def test_anatomy_structures_keep_organs_and_tumours_only() -> None:
    """Check that the Structures tab keeps organs and tumours and drops needles.

    Fails if Applicator, BODY or a marker stays in the tuple, or if Bladder or
    GTV is dropped. Needle paths already live on Channels; listing them here
    hides the anatomy the physicist came to show (FR-SV-01).
    """
    bladder = _structure(7, "Bladder", StructureType.ORGAN, (1, 2, 3))
    gtv = _structure(2, "GTV", StructureType.TUMOUR, (200, 0, 0))
    applicator = _structure(34, "Applicator26", StructureType.OTHER)
    body = _structure(1, "BODY", StructureType.OTHER)
    marker = _structure(3, "Surface3", StructureType.OTHER)

    assert anatomy_structures((applicator, bladder, body, gtv, marker)) == (bladder, gtv)
    assert anatomy_structures(None) == ()
    assert anatomy_structures(()) == ()
