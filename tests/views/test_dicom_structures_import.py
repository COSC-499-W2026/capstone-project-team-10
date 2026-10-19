"""Check that DICOM import attaches decoded structures onto DicomData."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from windows.main_window import MainWindow


def test_importing_ex1_fills_structures_on_dicom_data(
    channels_window: MainWindow,
) -> None:
    """Check that reading Ex1 through the vendor import path fills structures.

    channels_window loads Ex1 with read_dicom_folder, the same call Import uses.
    Fails if structures is None or not 42 ROIs, or if the first is not BODY.
    That is what happens when load_structures is dropped from the Varian reader,
    which would leave the Import list and later visualisation with nothing to show
    (issue #40).
    """
    structures = channels_window.dicommodel.data.structures

    assert structures is not None
    assert len(structures) == 42
    assert structures[0].name == "BODY"
