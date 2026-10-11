"""Behavioral tests for reading anatomical RTSTRUCT contours."""

import pytest
from pydicom.dataset import Dataset

from classes.dicom.structures import StructureReadError, StructureType, read_structures


def structure_set() -> Dataset:
    """Build a real in-memory RTSTRUCT fixture, not a mock.

    Its deliberately shuffled ROI records expose positional joins through wrong
    names, colours, or contours, preventing anatomy from being misidentified.
    """
    dataset = Dataset()
    dataset.Modality = "RTSTRUCT"
    definitions = []
    contours = []
    observations = []
    for number, name, kind in [(7, "Bladder", "ORGAN"), (2, "Target", "CTV")]:
        definition = Dataset()
        definition.ROINumber = number
        definition.ROIName = name
        definition.ReferencedFrameOfReferenceUID = "1.2.3"
        definitions.append(definition)
        roi = Dataset()
        roi.ReferencedROINumber = number
        roi.ROIDisplayColor = [255, 128, 0] if number == 7 else [255, 0, 0]
        slices = []
        for height in [0, 5]:
            contour = Dataset()
            contour.ContourGeometricType = "CLOSED_PLANAR"
            contour.NumberOfContourPoints = 3
            contour.ContourData = [0, 0, height, 4, 0, height, 0, 3, height]
            slices.append(contour)
        roi.ContourSequence = slices
        contours.append(roi)
        observation = Dataset()
        observation.ReferencedROINumber = number
        observation.RTROIInterpretedType = kind
        observations.append(observation)
    dataset.StructureSetROISequence = definitions
    dataset.ROIContourSequence = list(reversed(contours))
    dataset.RTROIObservationsSequence = list(reversed(observations))
    return dataset


def test_join_by_identifier_and_keep_all_slices() -> None:
    """Read both slices and join metadata by ROI number.

    Positional joins or reading only the first slice fail the literal assertions,
    preventing mislabelled or incomplete anatomy from reaching visualization.
    """
    bladder, target = read_structures(structure_set())
    assert (bladder.roi_number, bladder.name, bladder.category) == (7, "Bladder", StructureType.ORGAN)
    assert bladder.color == (255, 128, 0)
    assert bladder.frame_of_reference_uid == "1.2.3"
    assert bladder.contours[1].points == ((0.0, 0.0, 5.0), (4.0, 0.0, 5.0), (0.0, 3.0, 5.0))
    assert len(bladder.contours) == 2
    assert target.category == StructureType.TUMOUR
    assert target.interpreted_type == "CTV"
    assert bladder.contours[0].geometric_type == "CLOSED_PLANAR"


def test_optional_metadata_and_duplicate_names() -> None:
    """Keep duplicate names distinct and supply defaults for absent optional metadata.

    Keying structures by name or requiring colour and observations fails these
    assertions, preventing valid structures from disappearing on import.
    """
    dataset = structure_set()
    dataset.StructureSetROISequence[1].ROIName = "Bladder"
    del dataset.ROIContourSequence[1].ROIDisplayColor
    del dataset.RTROIObservationsSequence
    structures = read_structures(dataset)
    assert [roi.roi_number for roi in structures] == [7, 2]
    assert [roi.name for roi in structures] == ["Bladder", "Bladder"]
    assert structures[0].color == (128, 128, 128)
    assert structures[0].category == StructureType.OTHER
    assert structures[0].interpreted_type is None


def test_metadata_only_structure_is_retained() -> None:
    """Retain a defined ROI that has no contour geometry.

    Dropping such ROIs fails the empty-contour assertion; keeping their metadata
    lets a future UI explain why a structure cannot be displayed.
    """
    dataset = structure_set()
    del dataset.ROIContourSequence
    assert read_structures(dataset)[0].contours == ()


@pytest.mark.parametrize("kind,count,coordinates", [
    ("POINT", 1, [1, 2, 3]),
    ("OPEN_PLANAR", 2, [0, 0, 0, 1, 0, 0]),
    ("OPEN_NONPLANAR", 2, [0, 0, 0, 1, 2, 3]),
    ("CLOSEDPLANAR_XOR", 3, [0, 0, 0, 4, 0, 0, 0, 3, 0]),
])
def test_preserve_contour_semantics(kind: str, count: int, coordinates: list[int]) -> None:
    """Preserve supported contour types without treating every ROI as a solid.

    Rewriting open contours or XOR contours as ordinary polygons fails the type
    assertion, preventing later reconstruction from silently filling wrong regions.
    """
    dataset = structure_set()
    contour = dataset.ROIContourSequence[0].ContourSequence[0]
    contour.ContourGeometricType = kind
    contour.NumberOfContourPoints = count
    contour.ContourData = coordinates
    dataset.ROIContourSequence[0].ContourSequence = [contour]
    parsed = read_structures(dataset)[1].contours[0]
    assert parsed.geometric_type == kind
    assert len(parsed.points) == count


@pytest.mark.parametrize("coordinates,count", [
    ([0, 0, 0, 1], 3),
    ([0, 0, 0, 4, 0, 0, 0, 3, 0], 4),
    ([0, 0, 0, 4, 0, 0, 0, float("nan"), 0], 3),
    ([0, 0, 0, 4, 0, 0, 0, float("inf"), 0], 3),
    ([0, 0, 0, 1, 1, 1], 2),
])
def test_reject_malformed_coordinates(coordinates: list[float], count: int) -> None:
    """Reject incomplete, nonfinite, or incorrectly counted contour points.

    Removing validation fails the expected StructureReadError, preventing invalid
    spatial coordinates from being passed into the geometry kernel.
    """
    dataset = structure_set()
    contour = dataset.ROIContourSequence[0].ContourSequence[0]
    contour.ContourData = coordinates
    contour.NumberOfContourPoints = count
    with pytest.raises(StructureReadError, match="ROI 2"):
        read_structures(dataset)


@pytest.mark.parametrize("sequence", ["ROIContourSequence", "RTROIObservationsSequence"])
def test_reject_orphan_references(sequence: str) -> None:
    """Reject records referencing a structure that was never defined.

    Silently dropping an orphan fails the expected error; rejecting the import
    prevents an incomplete anatomical dataset from being mistaken for a full one.
    """
    dataset = structure_set()
    dataset[sequence].value[0].ReferencedROINumber = 99
    with pytest.raises(StructureReadError, match="99"):
        read_structures(dataset)


def test_reject_duplicate_identifiers() -> None:
    """Reject ambiguous ROI identifiers instead of overwriting one structure.

    Duplicate identifiers must raise StructureReadError, preventing two distinct
    organs from being assigned the same geometry.
    """
    dataset = structure_set()
    dataset.StructureSetROISequence[1].ROINumber = 7
    with pytest.raises(StructureReadError, match="7"):
        read_structures(dataset)


@pytest.mark.parametrize("color", [[256, 0, 0], [-1, 0, 0], [255, 0]])
def test_reject_invalid_color(color: list[int]) -> None:
    """Reject malformed RGB triples with a domain error.

    Missing length or range checks fail the expected exception, preventing invalid
    colour values from reaching renderer controls.
    """
    dataset = structure_set()
    dataset.ROIContourSequence[0].ROIDisplayColor = color
    with pytest.raises(StructureReadError, match="ROI 2"):
        read_structures(dataset)


def test_reject_wrong_modality_and_missing_definitions() -> None:
    """Require an RTSTRUCT dataset with a definition sequence.

    Treating another modality or missing definitions as an empty valid import fails
    the expected errors, preventing an invalid selection from replacing anatomy.
    """
    dataset = structure_set()
    dataset.Modality = "RTPLAN"
    with pytest.raises(StructureReadError):
        read_structures(dataset)
    dataset.Modality = "RTSTRUCT"
    del dataset.StructureSetROISequence
    with pytest.raises(StructureReadError):
        read_structures(dataset)


def test_reject_mixed_xor_contours() -> None:
    """Require XOR semantics for every contour when any contour uses XOR.

    Accepting mixed ordinary and XOR polygons fails the expected error and could
    cause a later reconstructor to fill an anatomical hole incorrectly.
    """
    dataset = structure_set()
    dataset.ROIContourSequence[0].ContourSequence[0].ContourGeometricType = "CLOSEDPLANAR_XOR"
    with pytest.raises(StructureReadError, match="ROI 2"):
        read_structures(dataset)


@pytest.mark.parametrize("sequence", ["ROIContourSequence", "RTROIObservationsSequence"])
def test_reject_ambiguous_records(sequence: str) -> None:
    """Reject repeated records for one ROI rather than silently selecting one.

    Overwriting an existing record fails the expected error, protecting metadata
    and geometry from order-dependent loss.
    """
    dataset = structure_set()
    dataset[sequence].value.append(dataset[sequence].value[0])
    with pytest.raises(StructureReadError, match="2"):
        read_structures(dataset)


def test_preserve_input_and_unknown_type() -> None:
    """Preserve the original dataset and retain an unclassified interpreted type.

    In-place point edits or discarding unknown classification metadata fail these
    assertions, preserving source evidence for later geometry and display work.
    """
    from copy import deepcopy

    dataset = structure_set()
    dataset.RTROIObservationsSequence[0].RTROIInterpretedType = "EXTERNAL"
    original = deepcopy(dataset)
    result = read_structures(dataset)
    assert result[1].category == StructureType.OTHER
    assert result[1].interpreted_type == "EXTERNAL"
    assert dataset == original


def test_require_frame_of_reference() -> None:
    """Reject structures whose spatial reference is missing.

    Accepting missing frame metadata fails the expected error, preventing anatomy
    from being overlaid on needles without a known coordinate frame.
    """
    dataset = structure_set()
    del dataset.StructureSetROISequence[0].ReferencedFrameOfReferenceUID
    with pytest.raises(StructureReadError, match="ROI 7"):
        read_structures(dataset)
