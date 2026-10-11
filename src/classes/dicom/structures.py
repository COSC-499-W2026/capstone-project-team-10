"""Read RTSTRUCT anatomy independently of Qt and OpenCASCADE."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite

from pydicom.dataset import Dataset


class StructureReadError(ValueError):
    """An RTSTRUCT cannot be decoded without losing or misidentifying geometry."""


class StructureType(Enum):
    TUMOUR = "tumour"
    ORGAN = "organ"
    OTHER = "other"


@dataclass(frozen=True)
class Contour:
    """One contour in patient coordinates, in millimetres.

    The geometric type is retained so open paths and XOR boundaries cannot be
    mistaken for ordinary closed polygons by a future surface builder.
    """

    geometric_type: str
    points: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class Structure:
    """An ROI and its contours, independent of rendering and display state.

    Colours are DICOM RGB integers in 0..255. Empty contours mean that no geometry
    was supplied, not that a reconstruction succeeded. Category TUMOUR groups
    GTV, CTV and PTV planning volumes; it does not assert that all are tumour tissue.
    """

    roi_number: int
    name: str
    frame_of_reference_uid: str
    color: tuple[int, int, int]
    interpreted_type: str | None
    category: StructureType
    contours: tuple[Contour, ...]


def _index_records(records: list[Dataset], known_rois: set[int], label: str) -> dict[int, Dataset]:
    """Reject dangling or ambiguous references before joining ROI records."""
    indexed: dict[int, Dataset] = {}
    for record in records:
        number = int(str(record.ReferencedROINumber))
        if number not in known_rois:
            raise StructureReadError(f"{label} references unknown ROI {number}")
        if number in indexed:
            raise StructureReadError(f"Duplicate {label} for ROI {number}")
        indexed[number] = record
    return indexed


def _read_contour(record: Dataset) -> Contour:
    """Decode a supported contour without interpolating or modifying its points."""
    kind = str(record.ContourGeometricType)
    minimum_points = {
        "POINT": 1,
        "OPEN_PLANAR": 2,
        "OPEN_NONPLANAR": 2,
        "CLOSED_PLANAR": 3,
        "CLOSEDPLANAR_XOR": 3,
    }
    if kind not in minimum_points:
        raise StructureReadError(f"Unsupported contour type {kind}")
    count = int(str(record.NumberOfContourPoints))
    coordinates = tuple(float(value) for value in record.ContourData)
    if len(coordinates) != count * 3 or count < minimum_points[kind]:
        raise StructureReadError("Invalid contour point count")
    if kind == "POINT" and count != 1:
        raise StructureReadError("POINT must contain exactly one point")
    if not all(isfinite(value) for value in coordinates):
        raise StructureReadError("Contour coordinates must be finite")
    points = tuple(
        (coordinates[index], coordinates[index + 1], coordinates[index + 2])
        for index in range(0, len(coordinates), 3)
    )
    return Contour(kind, points)


def _read_structure(definition: Dataset, geometry: Dataset, observation: Dataset) -> Structure:
    """Decode one ROI with defaults only for optional display metadata."""
    number = int(str(definition.ROINumber))
    frame_uid = str(definition.ReferencedFrameOfReferenceUID).strip()
    if not frame_uid:
        raise StructureReadError("Missing frame of reference UID")
    color_values = tuple(int(str(value)) for value in geometry.get("ROIDisplayColor", [128, 128, 128]))
    if len(color_values) != 3 or any(value < 0 or value > 255 for value in color_values):
        raise StructureReadError("Colour must contain three integers in 0..255")
    raw_type = observation.get("RTROIInterpretedType")
    interpreted_type = str(raw_type).strip().upper() if raw_type else None
    category = StructureType.OTHER
    if interpreted_type in {"GTV", "CTV", "PTV"}:
        category = StructureType.TUMOUR
    elif interpreted_type == "ORGAN":
        category = StructureType.ORGAN
    contours = tuple(_read_contour(record) for record in geometry.get("ContourSequence", []))
    kinds = {contour.geometric_type for contour in contours}
    if "CLOSEDPLANAR_XOR" in kinds and len(kinds) != 1:
        raise StructureReadError("XOR contours cannot be mixed with other contour types")
    return Structure(
        number,
        str(definition.ROIName),
        frame_uid,
        (color_values[0], color_values[1], color_values[2]),
        interpreted_type,
        category,
        contours,
    )


def read_structures(dataset: Dataset) -> tuple[Structure, ...]:
    """Read all ROIs from a pydicom RTSTRUCT dataset, in definition order.

    Join by ROI number, never by sequence position or name. Invalid metadata or
    contours raise StructureReadError and no partial result is returned. The input
    dataset is not changed. Missing optional colour uses neutral grey; missing or
    unrecognized interpreted types use OTHER. Geometry-free ROIs are retained.

    This is a decoding boundary, not a surface validator. It does not check polygon
    planarity, self-intersection, or reconstruct solids. Coordinates remain in the
    recorded patient frame, with no cylinder transform or dead-space correction.
    """
    try:
        if dataset.get("Modality") != "RTSTRUCT":
            raise StructureReadError("Expected an RTSTRUCT dataset")
        definitions = dataset.StructureSetROISequence
        known_rois: set[int] = set()
        for definition in definitions:
            number = int(str(definition.ROINumber))
            if number in known_rois:
                raise StructureReadError(f"Duplicate definition for ROI {number}")
            known_rois.add(number)
        geometries = _index_records(dataset.get("ROIContourSequence", []), known_rois, "contours")
        observations = _index_records(dataset.get("RTROIObservationsSequence", []), known_rois, "observations")
        structures = []
        for definition in definitions:
            number = int(str(definition.ROINumber))
            try:
                structures.append(_read_structure(
                    definition, geometries.get(number, Dataset()), observations.get(number, Dataset())
                ))
            except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as error:
                raise StructureReadError(f"ROI {number}: {error}") from error
        return tuple(structures)
    except StructureReadError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as error:
        raise StructureReadError(f"Malformed RTSTRUCT: {error}") from error
