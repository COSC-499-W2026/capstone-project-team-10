"""Exercise rounded_channel's reuse of a solid it already built from the same inputs."""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.Core.GProp import GProp_GProps

if TYPE_CHECKING:
    from OCC.Core.TopoDS import TopoDS_Shape

    from classes.app import RadiotherapyApp
    from classes.mesh.channel import ChannelKey

BENT = [[0.0, 0.0, 100.0], [0.0, 0.0, 50.0], [10.0, 0.0, 20.0]]
PLANTED = [[2.0, 3.0, 100.0], [2.0, 3.0, 50.0], [12.0, 3.0, 20.0]]
FLAT_LAST_PIPE = [[0.0, 0.0, 100.0], [0.0, 0.0, 50.0], [30.0, 0.0, 50.0]]
MARKER_VOLUME = 4.18879  # a sphere of radius 1 mm, which no channel build makes


class ChannelProblems:
    """Stand in for the main window's two channel dialogs and record each call. A helper, not a test.

    rounded_channel reports a channel it could not build cleanly through
    get_app().window.channel_display_warning() and channel_display_error(), which open a
    QMessageBox in the real window. Recording the calls shows whether a build ran and was reported.
    """

    def __init__(self) -> None:
        """Start with no calls recorded."""
        self.calls: list[str] = []

    def channel_display_warning(self) -> None:
        """Record a warning, as MainWindow.channel_display_warning would show one."""
        self.calls.append("warning")

    def channel_display_error(self) -> None:
        """Record an error, as MainWindow.channel_display_error would show one."""
        self.calls.append("error")


@pytest.fixture
def problems(geometry_app: RadiotherapyApp, default_settings: dict[str, float]) -> Iterator[ChannelProblems]:
    """Put a ChannelProblems where rounded_channel looks for the window, then put the window back. A fixture, not a test."""
    previous = geometry_app.window
    geometry_app.window = ChannelProblems()
    yield geometry_app.window
    geometry_app.window = previous


def volume(solid: TopoDS_Shape) -> float:
    """Return a solid's volume in mm cubed, to 5 places. A helper, not a test."""
    properties = GProp_GProps()
    brepgprop.VolumeProperties(solid, properties)
    return round(properties.Mass(), 5)


def plant_marker(settings: dict[str, float]) -> None:
    """Keep a 1 mm sphere in the store as the solid for PLANTED at offset 0 and diameter 3. A helper, not a test.

    A build never makes that sphere, so a result with its volume came from the store and a
    result without it was built.
    """
    from classes.mesh.channel import ChannelSettings, built_channels, channel_key

    key = channel_key(PLANTED, 0.0, 3.0, ChannelSettings.from_config(settings))
    built_channels.keep(key, BRepPrimAPI_MakeSphere(1.0).Shape())


def test_the_same_inputs_are_given_the_kept_solid_instead_of_a_new_build(default_settings: dict[str, float]) -> None:
    """Check rounded_channel returns the solid kept for identical points, offset, diameter and settings.

    Fails if it builds again, which runs the 30-odd fuses that made every plan import take
    about 9 seconds.
    """
    from classes.mesh.channel import rounded_channel

    plant_marker(default_settings)

    assert volume(rounded_channel([list(point) for point in PLANTED], 0.0, 3.0)) == MARKER_VOLUME


def test_each_call_gets_its_own_copy_with_the_same_geometry(default_settings: dict[str, float]) -> None:
    """Check two calls with identical inputs return solids that are not the same shape but have the same volume.

    Fails if both get the one kept solid. The viewport picks a channel by matching shapes, so
    two identical applicators would share one shape and a click on the second would select the
    first. Fails too if the copy is not the kept geometry.
    """
    from classes.mesh.channel import rounded_channel

    first, second = rounded_channel(BENT, 5.0, 3.0), rounded_channel(BENT, 5.0, 3.0)

    assert not first.IsSame(second)
    assert volume(first) == volume(second) > 0


@pytest.mark.parametrize(
    "setting, value",
    [
        ("CONFIG_DEADSPACE", 4.0),
        ("CONFIG_CHANNELS_THREADING_DEPTH", 3.0),
        ("CONFIG_CHANNELS_THREADING_DIAMETER", 2.0),
    ],
)
def test_a_changed_setting_is_built_instead_of_given_the_kept_solid(default_settings: dict[str, float], setting: str, value: float) -> None:
    """Check changing the deadspace or either threading setting builds a channel instead of reusing the kept one.

    Fails if a setting the build reads is left out of what rounded_channel compares. The
    viewport and the exported model would then keep the old tip or thread after the clinician
    changed it, and the printed applicator would not match the settings on screen.
    """
    from classes.mesh.channel import rounded_channel

    plant_marker(default_settings)
    default_settings[setting] = value

    assert volume(rounded_channel(PLANTED, 0.0, 3.0)) != MARKER_VOLUME


@pytest.mark.parametrize(
    "points, offset, diameter",
    [
        ([[2.0, 3.0, 100.0], [2.0, 3.0, 50.0], [12.5, 3.0, 20.0]], 0.0, 3.0),
        (PLANTED, 0.5, 3.0),
        (PLANTED, 0.0, 3.5),
    ],
    ids=["points", "offset", "diameter"],
)
def test_a_changed_argument_is_built_instead_of_given_the_kept_solid(
    default_settings: dict[str, float], points: list[list[float]], offset: float, diameter: float
) -> None:
    """Check a different point, offset or diameter builds a channel instead of reusing the kept one.

    Fails if an argument is left out of what rounded_channel compares, so a moved needle, a
    changed cylinder length or a new diameter would show and export the previous hole.
    """
    from classes.mesh.channel import rounded_channel

    plant_marker(default_settings)

    assert volume(rounded_channel(points, offset, diameter)) != MARKER_VOLUME


def test_a_channel_that_reported_a_problem_is_built_and_reported_again(problems: ChannelProblems) -> None:
    """Check a channel whose build opened an error dialog is not reused, so the second build reports it too.

    A flat last pipe makes the corner fuse fail every time. Fails if that solid were kept, so a
    reimported plan showed the broken channel without the dialog that tells the clinician the
    hole may be incomplete, and they would print it unwarned.
    """
    from classes.mesh.channel import rounded_channel

    rounded_channel(FLAT_LAST_PIPE, 0.0, 3.0)
    first = list(problems.calls)
    rounded_channel(FLAT_LAST_PIPE, 0.0, 3.0)

    assert first and problems.calls == first + first


def key(z: float) -> ChannelKey:
    """Return a ChannelKey for a one-point channel at height z, at the default settings. A helper, not a test."""
    from classes.mesh.channel import ChannelSettings

    return (((0.0, 0.0, z),), 0.0, 3.0, ChannelSettings(deadspace=6.0, threading_depth=5.0, threading_diameter=3.17))


def test_the_least_recently_used_solid_is_dropped_once_the_store_is_full(geometry_app: RadiotherapyApp) -> None:
    """Check a store of two keeps the two solids used last, and drops the one used longest ago.

    Fails if the store grows without limit, so dragging the cylinder length through many values
    would keep every needle at every length in memory, or if it drops a solid that was just
    looked up, so going back and forth between two lengths would rebuild each time.
    """
    from classes.mesh.channel import ChannelSolids

    store = ChannelSolids(capacity=2)
    first, second, third = (BRepPrimAPI_MakeSphere(radius).Shape() for radius in (1.0, 2.0, 3.0))
    store.keep(key(1.0), first)
    store.keep(key(2.0), second)
    looked_up = store.get(key(1.0))
    store.keep(key(3.0), third)

    assert looked_up is first
    assert store.get(key(1.0)) is first and store.get(key(3.0)) is third
    assert store.get(key(2.0)) is None
