"""Attach Gilles's RTSTRUCT decode onto DicomData without pulling in the vendor readers."""

from pydicom.dataset import Dataset

from classes.dicom.data import DicomData
from classes.dicom.structures import StructureReadError, read_structures
from classes.logger import log


def load_structures(data: DicomData, rs_dataset: Dataset) -> None:
    """Fill data.structures from an RTSTRUCT dataset.

    On StructureReadError, set structures to None so a failed decode cannot leave
    another plan's anatomy active. Needle and cylinder loading stay independent.
    """
    try:
        data.structures = read_structures(rs_dataset)
    except StructureReadError as error:
        log.error(f"Reading RTSTRUCT anatomy failed: {error}")
        data.structures = None
