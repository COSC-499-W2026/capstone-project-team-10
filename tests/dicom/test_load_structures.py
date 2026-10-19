"""Exercise attaching Gilles's RTSTRUCT reader result onto DicomData during import."""

import pytest

pydicom = pytest.importorskip("pydicom")
from pydicom.dataset import Dataset

from classes.dicom.data import DicomData
from classes.dicom.load_structures import load_structures
from classes.dicom.structures import StructureType


def organ_structure_set() -> Dataset:
    """Helper, not a test. One ORGAN ROI so a load result is a known literal.

    Built as a real Dataset, not a mock, so load_structures exercises the same decode
    path import will use.
    """
    dataset = Dataset()
    dataset.Modality = "RTSTRUCT"
    definition = Dataset()
    definition.ROINumber = 7
    definition.ROIName = "Bladder"
    definition.ReferencedFrameOfReferenceUID = "1.2.3"
    dataset.StructureSetROISequence = [definition]
    geometry = Dataset()
    geometry.ReferencedROINumber = 7
    geometry.ROIDisplayColor = [255, 128, 0]
    contour = Dataset()
    contour.ContourGeometricType = "CLOSED_PLANAR"
    contour.NumberOfContourPoints = 3
    contour.ContourData = [0, 0, 0, 4, 0, 0, 0, 3, 0]
    geometry.ContourSequence = [contour]
    dataset.ROIContourSequence = [geometry]
    observation = Dataset()
    observation.ReferencedROINumber = 7
    observation.RTROIInterpretedType = "ORGAN"
    dataset.RTROIObservationsSequence = [observation]
    return dataset


def test_load_structures_fills_dicom_data_from_rtstruct() -> None:
    """Check that load_structures stores the decoded ROIs on DicomData.structures.

    Fails if structures stays None or the bladder name, colour or category is wrong.
    Import must expose Gilles's reader result on the form the rest of the app reads, or
    the structure list and later visualisation have nothing to show.
    """
    data = DicomData()
    load_structures(data, organ_structure_set())
    assert data.structures is not None
    assert len(data.structures) == 1
    bladder = data.structures[0]
    assert (bladder.roi_number, bladder.name, bladder.category) == (
        7,
        "Bladder",
        StructureType.ORGAN,
    )
    assert bladder.color == (255, 128, 0)


def test_load_structures_clears_structures_when_decode_fails() -> None:
    """Check that a StructureReadError leaves DicomData.structures as None.

    Fails if a previous value survives or a partial tuple is kept. FR-SV-01 requires that
    a failed structure read does not leave half-imported anatomy active for the next plan.
    """
    data = DicomData()
    data.structures = ("left over from a previous decode",)
    bad = Dataset()
    bad.Modality = "RTPLAN"
    load_structures(data, bad)
    assert data.structures is None
