from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

if TYPE_CHECKING:
    from windows.main_window import MainWindow

CHANNELS_TAB = 2


def channel_label(window: MainWindow, index: int) -> str:
    """Return the label of the index-th imported channel, as a helper and not a test.

    The module shares one window, so each test moves a channel of its own, and a move left
    behind by one test cannot change what another test measures.
    """
    return list(window.channelsmodel.channels)[index]


def plan_points(window: MainWindow, label: str) -> list[list[float]]:
    """Return a channel's DICOM points as plain floats, as a helper and not a test."""
    return [[float(value) for value in point] for point in window.channelsmodel.channels[label].points_raw]


@contextmanager
def marked_as_tandem(window: MainWindow, label: str) -> Iterator[None]:
    """Mark a channel as the plan's tandem for one block and then restore the plan, as a helper and not a test.

    It sets only the plan's tandem label, which is what the model reads to refuse a move, and
    puts the old label back on exit so the module's shared window is left as it was found.
    """
    data = window.dicommodel.data
    previous = data.tandem_channel
    data.tandem_channel = label
    try:
        yield
    finally:
        data.tandem_channel = previous


class StubbedAnswer:
    """Stand in for the move popup, as a helper and not a test.

    Assigned to ChannelsView.ask_translation, the view's seam for its dialog, so no module is
    patched. It records each question asked and gives the chosen answer, None meaning Cancel.
    """

    def __init__(self, answer: tuple[float, float, float] | None) -> None:
        """Remember the answer to give, None meaning Cancel. A helper, not a test."""
        self.answer = answer
        self.asked: list[tuple[str, tuple[float, float, float]]] = []

    def __call__(self, label: str, translation: tuple[float, float, float]) -> tuple[float, float, float] | None:
        """Record the question the view asks and return the chosen answer. A helper, not a test."""
        self.asked.append((label, translation))
        return self.answer


def double_click_row(window: MainWindow, label: str, answer: tuple[float, float, float] | None) -> StubbedAnswer:
    """Emit the list's double-click signal for one channel's row and return what the popup was asked.

    A helper, not a test. It emits itemDoubleClicked, the signal a double click emits, because
    the list is never shown offscreen and so has no row to click.
    """
    view = window.navigationmodel.views[CHANNELS_TAB]
    stub = view.ask_translation = StubbedAnswer(answer)
    row = view.ui.listwidget_channels.findItems(label, Qt.MatchFlag.MatchExactly)[0]
    view.ui.listwidget_channels.itemDoubleClicked.emit(row)
    return stub


def test_moving_a_channel_shifts_every_point_and_leaves_the_dicom_points(channels_window: MainWindow) -> None:
    """Check a move adds (dx, dy, dz) to every point of the channel and never touches the DICOM points.

    Fails if any point is not shifted by exactly (1.5, -2, 0.5), or if points_raw, the plan's own
    points, changes. The Export cut and the PDF read the shifted points, so a wrong shift
    puts the needle hole in the wrong place on a patient's applicator, and a changed
    plan point would survive a re-import.
    """
    label = channel_label(channels_window, 0)
    before = plan_points(channels_window, label)

    channels_window.channelsmodel.move_channel(label, 1.5, -2.0, 0.5)

    channel = channels_window.channelsmodel.channels[label]
    assert [list(point) for point in channel.points] == [[x + 1.5, y - 2.0, z + 0.5] for x, y, z in before]
    assert plan_points(channels_window, label) == before


def test_a_move_reaches_the_pdf_points_and_the_3d_shape(channels_window: MainWindow) -> None:
    """Check the PDF's point reader and the channel's 3D shape both follow a move of 5 mm in X.

    Fails if the first point the PDF reads is not the plan point plus 5 mm in X, or if the
    shape's bounding box does not shift by 5 mm (to 0.05 mm). The Export cut uses this same
    shape, so a shape that ignored the move would leave the printed hole where the plan had it.
    """
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib

    from classes.pdf.template_reference import extract_points_from_channels2

    def x_bounds(shape) -> tuple[float, float]:
        """Return a shape's lowest and highest X from its OpenCASCADE bounding box. A helper, not a test."""
        box = Bnd_Box()
        brepbndlib.Add(shape, box)
        low_x, _, _, high_x, _, _ = box.Get()
        return low_x, high_x

    label = channel_label(channels_window, 1)
    channel = channels_window.channelsmodel.channels[label]
    first_plan_point = plan_points(channels_window, label)[0]
    low_before, high_before = x_bounds(channel.shape())

    channels_window.channelsmodel.move_channel(label, 5.0, 0.0, 0.0)

    first_pdf_point = extract_points_from_channels2([channel])[0][0]
    low_after, high_after = x_bounds(channel.shape())
    assert [float(value) for value in first_pdf_point] == [first_plan_point[0] + 5.0, first_plan_point[1], first_plan_point[2]]
    assert low_after - low_before == pytest.approx(5.0, abs=0.05)
    assert high_after - high_before == pytest.approx(5.0, abs=0.05)


def test_moving_a_channel_keeps_the_tandems_rotation_source(channels_window: MainWindow) -> None:
    """Check get_rotation gives the same angle after a move, because it reads the plan point.

    Fails if the angle changes. The tandem is aimed with this angle, so an angle read from a
    moved tip would turn the tandem away from the direction the clinician planned.
    """
    channel = channels_window.channelsmodel.channels[channel_label(channels_window, 2)]
    before = channel.get_rotation()

    channels_window.channelsmodel.move_channel(channel.label, 10.0, 10.0, 0.0)

    assert channel.get_rotation() == before


def test_a_rejected_move_keeps_the_previous_one(channels_window: MainWindow) -> None:
    """Check NaN and infinity raise ValueError and leave the earlier move in place.

    After a valid move, moving by NaN must not reset or half-apply it. Fails if no error is
    raised or the channel's translation changes. FR-CN-02 says an invalid edit is rejected
    and the previous state kept, since a silent reset would move a needle nobody chose to move.
    """
    model = channels_window.channelsmodel
    label = channel_label(channels_window, 3)
    model.move_channel(label, 1.0, 2.0, 3.0)

    for bad in (float("nan"), float("inf")):
        with pytest.raises(ValueError):
            model.move_channel(label, bad, 0.0, 0.0)

    assert model.channels[label].translation == (1.0, 2.0, 3.0)


@pytest.mark.parametrize("label", ["Missing channel", None])
def test_an_unknown_channel_cannot_be_moved(channels_window: MainWindow, label: str | None) -> None:
    """Check an unknown or unselected channel raises KeyError before any move is stored.

    Fails if no KeyError is raised or any channel ends up moved. A move stored under no real
    channel could later land on a different channel with that label.
    """
    model = channels_window.channelsmodel
    before = {name: channel.translation for name, channel in model.channels.items()}

    with pytest.raises(KeyError):
        model.move_channel(label, 1.0, 0.0, 0.0)

    assert {name: channel.translation for name, channel in model.channels.items()} == before


def test_the_tandem_channel_cannot_be_moved(channels_window: MainWindow) -> None:
    """Check the channel marked as the tandem refuses a move with ValueError.

    Fails if the move is accepted. The tandem is not cut as a needle and is aimed from its plan
    path, so a move would be invisible in the printed part and misleading on the screen.
    """
    label = channel_label(channels_window, 4)

    with marked_as_tandem(channels_window, label), pytest.raises(ValueError):
        channels_window.channelsmodel.move_channel(label, 1.0, 0.0, 0.0)

    assert not channels_window.channelsmodel.is_channel_moved(label)


def test_double_clicking_a_row_moves_the_channel_and_marks_the_row(channels_window: MainWindow) -> None:
    """Check double-clicking a row asks the popup, applies its answer and underlines the row.

    Fails if the popup is not asked with the channel's label and current move, the channel does
    not move, the row is not underlined, or its tooltip does not say how far it moved. A
    moved needle that looks like an untouched one hides a change to a patient device.
    """
    label = channel_label(channels_window, 5)
    view = channels_window.navigationmodel.views[CHANNELS_TAB]

    stub = double_click_row(channels_window, label, (1.5, -2.0, 0.5))

    row = view.ui.listwidget_channels.findItems(label, Qt.MatchFlag.MatchExactly)[0]
    assert stub.asked == [(label, (0.0, 0.0, 0.0))]
    assert channels_window.channelsmodel.channels[label].translation == (1.5, -2.0, 0.5)
    assert row.font().underline()
    assert "Moved by X 1.5, Y -2, Z 0.5 mm from the plan" in row.toolTip()


def test_cancelling_or_keeping_the_same_values_changes_nothing(channels_window: MainWindow) -> None:
    """Check Cancel, and OK with unchanged values, leave the channel and its built shape alone.

    Fails if the channel moves, or its cached shape is rebuilt (a rebuild takes about 0.6 s,
    so pressing OK with nothing edited would freeze the window for nothing).
    """
    label = channel_label(channels_window, 6)
    channel = channels_window.channelsmodel.channels[label]
    built = channel.shape()

    double_click_row(channels_window, label, None)
    double_click_row(channels_window, label, (0.0, 0.0, 0.0))

    assert not channels_window.channelsmodel.is_channel_moved(label)
    assert channel.shape() is built


def test_double_clicking_the_tandem_row_does_not_open_the_popup(channels_window: MainWindow) -> None:
    """Check the tandem channel's row never asks the popup.

    Fails if the popup is asked. It would offer a move the model must refuse.
    """
    label = channel_label(channels_window, 7)

    with marked_as_tandem(channels_window, label):
        stub = double_click_row(channels_window, label, (1.0, 0.0, 0.0))

    assert stub.asked == []


def test_the_popup_is_filled_with_the_current_move_and_reset_zeroes_it(channels_window: MainWindow) -> None:
    """Check the popup shows the current X, Y and Z, takes negative values, and Reset zeroes them.

    Fails if a field starts at another value, cannot hold -12.5 or 300, or Reset leaves a value
    behind. A spin box defaults to 0 to 99.99 mm, which would make a move toward negative
    coordinates impossible, and a wrong starting value would shift the needle on OK.
    """
    from windows.views.channels_view import MoveChannelDialog

    dialog = MoveChannelDialog("Applicator2", (1.0, -2.0, 3.0))
    assert dialog.translation() == (1.0, -2.0, 3.0)

    dialog.spin_x.setValue(-12.5)
    dialog.spin_z.setValue(300.0)
    assert dialog.translation() == (-12.5, -2.0, 300.0)

    QTest.mouseClick(dialog.btn_reset, Qt.MouseButton.LeftButton)
    assert dialog.translation() == (0.0, 0.0, 0.0)


def test_the_move_button_is_enabled_only_for_a_channel_that_can_be_moved(channels_window: MainWindow) -> None:
    """Check Move... is off with nothing selected, on for a needle, and off for the tandem channel.

    Fails if the button is enabled with no selection, disabled for an ordinary needle, or
    enabled for the tandem. With nothing selected it would open a popup for no channel, and
    for the tandem it would offer a move the model refuses.
    """
    model = channels_window.channelsmodel
    button = channels_window.navigationmodel.views[CHANNELS_TAB].ui.btn_move_channel
    label = channel_label(channels_window, 9)

    model.clear_selected_channels()
    assert not button.isEnabled()

    model.set_selected_channels(label)
    assert button.isEnabled()

    with marked_as_tandem(channels_window, label):
        model.update()
        assert not button.isEnabled()
    model.clear_selected_channels()


def test_pressing_the_move_button_moves_the_selected_channel(channels_window: MainWindow) -> None:
    """Check Move... asks the popup about the selected channel and applies its answer.

    Fails if the popup is not asked with the selected label and its current move, or the
    channel does not end up moved by the answer. The button is the discoverable way in for a
    physicist who does not know the row can be double-clicked.
    """
    label = channel_label(channels_window, 10)
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    channels_window.channelsmodel.set_selected_channels(label)
    stub = view.ask_translation = StubbedAnswer((2.0, 0.0, -1.5))

    QTest.mouseClick(view.ui.btn_move_channel, Qt.MouseButton.LeftButton)

    assert stub.asked == [(label, (0.0, 0.0, 0.0))]
    assert channels_window.channelsmodel.channels[label].translation == (2.0, 0.0, -1.5)
    channels_window.channelsmodel.clear_selected_channels()


def test_the_legend_explains_the_underline(channels_window: MainWindow) -> None:
    """Check the legend under the list says an underlined row has been moved, in copy a clinician can read.

    Fails if the legend does not say it, or contains a colon or an em dash, which the UI copy
    rule in AGENTS.md forbids. Without the line, the underline is a mark nobody can decode.
    """
    legend = channels_window.navigationmodel.views[CHANNELS_TAB].ui.label_channel_status_legend.text()

    assert "Underlined has been moved." in legend
    assert ":" not in legend and "—" not in legend


def sheet_diameter(window: MainWindow) -> float:
    """Return the cylinder's diameter, the one the reference sheet uses, as a helper and not a test."""
    return window.cylindermodel.cylinder.diameter


def test_a_needle_moved_out_of_the_cylinder_is_left_off_the_sheet_and_named(channels_window: MainWindow) -> None:
    """Check a needle moved 100 mm sideways is left off the sheet and named in the note.

    Fails if the needle is still counted inside the cylinder, if it is missing from the moved
    needles left off, or if the note does not name it. Without the note the sheet drops a
    needle the Export still cuts, and nobody reading the sheet would know it exists.
    """
    from classes.pdf.template_reference import channels_inside_cylinder, left_off_note, moved_channels_left_off

    label = channel_label(channels_window, 11)
    channels_window.channelsmodel.move_channel(label, 100.0, 0.0, 0.0)
    channels = channels_window.channelsmodel.get_visible_channels()
    diameter = sheet_diameter(channels_window)

    assert label not in [channel.label for channel in channels_inside_cylinder(channels, diameter)]
    assert label in [channel.label for channel in moved_channels_left_off(channels, diameter)]
    assert left_off_note([label]) == f"Moved needles left off this sheet because they no longer reach the base inside the cylinder, {label}."


def test_a_needle_moved_wholly_below_the_base_is_not_listed_with_a_zero_length(channels_window: MainWindow) -> None:
    """Check a needle moved 300 mm down, wholly below the base, is not counted inside the cylinder.

    Fails if it is still listed. A needle with no point above the base cuts no hole, and the
    sheet used to list it anyway, with a made-up point at the base and an extension of 0.0 cm.
    """
    from classes.pdf.template_reference import channels_inside_cylinder

    label = channel_label(channels_window, 0)
    channels_window.channelsmodel.move_channel(label, 0.0, 0.0, -300.0)

    inside = channels_inside_cylinder(channels_window.channelsmodel.get_visible_channels(), sheet_diameter(channels_window))

    assert label not in [channel.label for channel in inside]


def test_every_unmoved_needle_of_the_plan_stays_on_the_sheet(channels_window: MainWindow) -> None:
    """Check the needles nobody moved all still count as inside the cylinder.

    Fails if the new above-the-base rule drops an ordinary plan needle. Dropping one would
    silently remove a needle from the reference sheet of an untouched plan.
    """
    from classes.pdf.template_reference import channels_inside_cylinder, moved_channels_left_off

    unmoved = [channel for channel in channels_window.channelsmodel.get_visible_channels() if channel.translation == (0.0, 0.0, 0.0)]

    assert len(unmoved) >= 4
    assert channels_inside_cylinder(unmoved, sheet_diameter(channels_window)) == unmoved
    assert moved_channels_left_off(unmoved, sheet_diameter(channels_window)) == []


def test_the_note_has_no_colon_or_dash(channels_window: MainWindow) -> None:
    """Check the sheet's note follows the UI copy rule, with no colon and no em dash.

    Fails if either appears. The sheet is read by a clinician, so AGENTS.md forbids both in
    text written onto it.
    """
    from classes.pdf.template_reference import left_off_note

    note = left_off_note(["Applicator3", "Applicator5"])

    assert note.endswith("cylinder, Applicator3, Applicator5.")
    assert ":" not in note and "\u2014" not in note


def test_the_popup_warns_while_the_typed_move_would_leave_the_cylinder(channels_window: MainWindow) -> None:
    """Check the popup's warning shows for a move that leaves the cylinder and hides again for one that does not.

    Fails if the warning stays hidden after X is set to 60, keeps showing after X goes back to
    0, or the text is not the one given. The warning must follow the typed value, so a
    physicist sees it before pressing OK, and it must never stop OK.
    """
    from windows.views.channels_view import MoveChannelDialog

    dialog = MoveChannelDialog("Applicator2", (0.0, 0.0, 0.0), lambda move: "Warned" if move[0] > 50 else "")
    assert dialog.label_warning.isHidden()

    dialog.spin_x.setValue(60.0)
    assert not dialog.label_warning.isHidden() and dialog.label_warning.text() == "Warned"

    dialog.spin_x.setValue(0.0)
    assert dialog.label_warning.isHidden()


def test_the_popup_is_laid_out_to_grow_with_its_warning(channels_window: MainWindow) -> None:
    """Check the popup's layout resizes the dialog to its content, so a shown warning is not cut off.

    Fails if the layout's size constraint is not SetFixedSize. The warning appears after the
    popup is open, and without that constraint the running app kept the popup's first size
    and clipped the sentence to its first line, which a run of the real window showed.
    Offscreen, Qt resizes the dialog by itself and cannot reproduce the clipping, so this
    pins the setting that cures it and is not a measurement of the pixels.
    """
    from PySide6.QtWidgets import QLayout

    from windows.views.channels_view import MoveChannelDialog

    dialog = MoveChannelDialog("Applicator2", (0.0, 0.0, 0.0))

    assert dialog.layout().sizeConstraint() == QLayout.SizeConstraint.SetFixedSize


def test_a_move_out_of_the_cylinder_warns_in_the_view_and_the_row_tooltip(channels_window: MainWindow) -> None:
    """Check the view warns for a 100 mm move and not for none, and the moved row's tooltip carries it.

    Fails if the warning is empty for the 100 mm move, is not empty for no move, or the
    tooltip of a channel moved that far lacks it. A moved needle's problem has to be readable
    from the list, without opening the popup again.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    label = channel_label(channels_window, 3)

    assert view.warning_for(label, (0.0, 0.0, 0.0)) == ""
    assert view.warning_for(label, (100.0, 0.0, 0.0)) == "This needle no longer reaches the base inside the cylinder, so the reference sheet will not list it."

    channels_window.channelsmodel.move_channel(label, 100.0, 0.0, 0.0)
    row = view.ui.listwidget_channels.findItems(label, Qt.MatchFlag.MatchExactly)[0]
    assert "no longer reaches the base inside the cylinder" in row.toolTip()


def test_importing_a_plan_again_clears_every_move(channels_window: MainWindow) -> None:
    """Check a fresh load of the plan gives channels at their DICOM positions.

    Fails if any channel is still moved, or a plan point carries the earlier move. A move
    applied to a new patient's plan would put needles where nobody planned them. This
    rebuilds every channel, which takes several seconds, so it runs last in the module.
    """
    model = channels_window.channelsmodel
    label = channel_label(channels_window, 8)
    model.move_channel(label, 4.0, 4.0, 4.0)

    model.load_data(channels_window.dicommodel.data)

    assert all(not model.is_channel_moved(name) for name in model.channels)
    assert [list(point) for point in model.channels[label].points] == plan_points(channels_window, label)
