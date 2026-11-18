"""Pin the solid NeedleChannel builds for every channel of the two sample plans, at the default settings."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps

if TYPE_CHECKING:
    from OCC.Core.TopoDS import TopoDS_Shape

    from classes.app import RadiotherapyApp

pytestmark = pytest.mark.slow

REPO_ROOT = Path(__file__).resolve().parents[2]
EX1 = "SI_C_D30 Brachify_Ex1"
EX2 = "SI_C_D30 Brachify_Ex2"

type Measurement = tuple[float, float, float, float, float, float, float, float, float, float]

# Volume (mm^3), centre of mass (x, y, z), then the tight bounding box (xmin, ymin, zmin, xmax,
# ymax, zmax), in mm, measured on main at 22ac6a8 before any change to channel building.
# Ex2's applicators are Ex1's, so only its Tandem channel is listed for it.
EXPECTED: dict[tuple[str, str], Measurement] = {
    (EX1, "Applicator2"): (1020.746, 0.248, -8.573, 85.518, -1.315, -26.264, -1.0, 1.855, -4.969, 171.967),
    (EX1, "Applicator3"): (1022.285, 4.384, -7.396, 85.604, 1.795, -22.802, -1.0, 13.948, -4.058, 171.972),
    (EX1, "Applicator4"): (1022.524, 7.542, -4.592, 85.61, 4.225, -14.262, -1.0, 22.895, -1.966, 171.968),
    (EX1, "Applicator5"): (1022.243, 8.22, 0.3, 85.6, 4.615, -1.263, -1.0, 25.916, 1.907, 171.964),
    (EX1, "Applicator6"): (1022.3, 7.599, 4.429, 85.604, 4.255, 1.849, -1.0, 23.049, 13.928, 171.974),
    (EX1, "Applicator7"): (996.343, 3.724, 7.181, 83.675, 1.705, 4.84, -1.0, 8.928, 15.194, 171.179),
    (EX1, "Applicator8"): (996.019, 0.132, 8.547, 83.66, -1.465, 6.091, -1.0, 1.705, 17.576, 171.17),
    (EX1, "Applicator9"): (996.019, -4.244, 7.057, 83.661, -9.439, 4.72, -1.0, -2.225, 15.051, 171.175),
    (EX1, "Applicator10"): (1022.497, -7.257, 4.44, 85.609, -22.659, 1.829, -1.0, -3.935, 13.984, 171.971),
    (EX1, "Applicator11"): (1022.482, -8.36, 0.448, 85.607, -26.066, -1.163, -1.0, -4.755, 2.007, 171.964),
    (EX1, "Applicator12"): (1022.492, -7.681, -4.29, 85.608, -23.14, -13.75, -1.0, -4.335, -1.716, 171.968),
    (EX1, "Applicator13"): (1022.494, -4.262, -7.279, 85.608, -13.831, -22.676, -1.0, -1.645, -3.958, 171.967),
    (EX2, "Tandem"): (1183.335, 2.158, 0.377, 99.979, -0.445, -1.352, -1.0, 12.546, 2.033, 203.678),
}


def measure(solid: TopoDS_Shape) -> Measurement:
    """Return a solid's volume, centre of mass and tight bounding box, each to 3 places. A helper, not a test.

    The box is measured without the default gap and on the exact geometry, so it is the
    solid's own extent. Two channels that agree on all ten numbers have the same size and
    sit in the same place.
    """
    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    centre = properties.CentreOfMass()
    box = Bnd_Box()
    box.SetGap(0)
    brepbndlib.AddOptimal(solid, box, False, False)
    values = (properties.Mass(), centre.X(), centre.Y(), centre.Z(), *box.Get())
    return tuple(round(value, 3) for value in values)


@pytest.fixture(scope="module")
def built(geometry_app: RadiotherapyApp) -> Iterator[dict[tuple[str, str], Measurement]]:
    """Import Ex1 and Ex2, build each channel listed in EXPECTED at the default settings, and measure it.

    A fixture, not a test. It builds once for the module because the 13 channels take about
    13 seconds. The channels are built the way ChannelsModel.load_data builds them on import,
    as a NeedleChannel from the plan's points with no cylinder offset. The live settings are a
    copy of the defaults while it builds and are put back afterwards. Fails with an exception
    from the DICOM readers if a sample plan no longer loads.
    """
    from classes.dicom.fileio import read_dicom_folder
    from classes.mesh.channel import NeedleChannel
    from settings.defaults import DEFAULT_CONFIG_VALUES

    previous = geometry_app.values.config_values
    geometry_app.values.config_values = DEFAULT_CONFIG_VALUES.copy()
    measured: dict[tuple[str, str], Measurement] = {}
    for plan in (EX1, EX2):
        data = read_dicom_folder(str(REPO_ROOT / plan))
        for label, roi, number, points in zip(data.channels_labels, data.channels_rois, data.channel_numbers, data.channel_paths):
            if (plan, str(label)) in EXPECTED:
                measured[(plan, str(label))] = measure(NeedleChannel(str(roi), str(number), str(label), points).shape())
    yield measured
    geometry_app.values.config_values = previous


def test_every_listed_channel_is_in_its_plan(built: dict[tuple[str, str], Measurement]) -> None:
    """Check each plan still has every channel EXPECTED lists, so the test below compares all of them.

    Fails if a reader change drops or renames a channel, which would also leave it out of the
    printed applicator.
    """
    assert set(built) == set(EXPECTED)


@pytest.mark.parametrize("channel", sorted(EXPECTED), ids=lambda channel: f"{channel[0][-3:]}-{channel[1]}")
def test_a_sample_channel_keeps_its_volume_position_and_extent(
    built: dict[tuple[str, str], Measurement], channel: tuple[str, str]
) -> None:
    """Check a sample channel's solid has the volume, centre of mass and bounding box measured on main.

    Fails if a change to how channels are built moves a hole, changes its diameter or tip, or
    stretches it, by more than 0.01 mm or 0.01 mm^3. The channel is the hole cut into a
    printed applicator, so a needle would no longer follow the plan inside the patient.
    """
    assert built[channel] == pytest.approx(EXPECTED[channel], abs=0.01)
