from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from tests.views.test_move_channel import CHANNELS_TAB, channel_label, double_click_row, marked_as_tandem

if TYPE_CHECKING:
    from windows.main_window import MainWindow

ALT = Qt.KeyboardModifier.AltModifier
SHIFT = Qt.KeyboardModifier.ShiftModifier
CTRL = Qt.KeyboardModifier.ControlModifier
KEYPAD = Qt.KeyboardModifier.KeypadModifier
NONE = Qt.KeyboardModifier.NoModifier


@pytest.mark.parametrize(("key", "modifiers", "step"), [
    (Qt.Key.Key_Left, ALT, (-1.0, 0.0, 0.0)),
    (Qt.Key.Key_Right, ALT, (1.0, 0.0, 0.0)),
    (Qt.Key.Key_Up, ALT, (0.0, 1.0, 0.0)),
    (Qt.Key.Key_Down, ALT, (0.0, -1.0, 0.0)),
    (Qt.Key.Key_PageUp, ALT, (0.0, 0.0, 1.0)),
    (Qt.Key.Key_PageDown, ALT, (0.0, 0.0, -1.0)),
    (Qt.Key.Key_Up, ALT | CTRL, (0.0, 0.0, 1.0)),
    (Qt.Key.Key_Down, ALT | CTRL, (0.0, 0.0, -1.0)),
    (Qt.Key.Key_Left, ALT | SHIFT, (-0.1, 0.0, 0.0)),
    (Qt.Key.Key_PageUp, ALT | SHIFT, (0.0, 0.0, 0.1)),
    (Qt.Key.Key_Down, ALT | CTRL | SHIFT, (0.0, 0.0, -0.1)),
    (Qt.Key.Key_Right, ALT | KEYPAD, (1.0, 0.0, 0.0)),
])
def test_each_nudge_key_gives_its_axis_and_step(units_app, key: Qt.Key, modifiers: Qt.KeyboardModifier, step: tuple[float, float, float]) -> None:
    """Check every nudge key moves along the axis the issue's table gives, 1 mm, or 0.1 mm with Shift.

    Fails if a key gives the wrong axis, sign or size, or if the keypad flag macOS adds to
    arrow keys stops a nudge. A swapped axis or sign would move a needle of a patient device
    somewhere other than where the physicist pressed.
    """
    from windows.views.nudge_keys import nudge_step

    assert nudge_step(key, modifiers) == step


@pytest.mark.parametrize(("key", "modifiers"), [
    (Qt.Key.Key_Left, NONE),
    (Qt.Key.Key_Down, SHIFT),
    (Qt.Key.Key_Up, CTRL),
    (Qt.Key.Key_PageUp, NONE),
    (Qt.Key.Key_Left, ALT | CTRL),
    (Qt.Key.Key_A, ALT),
])
def test_keys_without_alt_or_outside_the_table_do_not_nudge(units_app, key: Qt.Key, modifiers: Qt.KeyboardModifier) -> None:
    """Check plain, Shift and Ctrl arrows, and other Alt keys, give no nudge.

    Fails if any of them gives a step. Plain and Shift arrows move and extend the list's
    selection, so taking them would break list navigation and move a needle by surprise.
    """
    from windows.views.nudge_keys import nudge_step

    assert nudge_step(key, modifiers) is None


@pytest.mark.parametrize(("current", "step", "expected"), [
    ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, -1.0, 0.0)),
    ((299.5, 0.0, 0.0), (1.0, 0.0, 0.0), (300.0, 0.0, 0.0)),
    ((0.0, -300.0, 2.0), (0.0, -0.1, 0.0), (0.0, -300.0, 2.0)),
    ((0.2, 0.0, 0.0), (0.1, 0.0, 0.0), (0.3, 0.0, 0.0)),
])
def test_a_nudge_adds_to_the_move_within_the_popups_range(units_app, current, step, expected) -> None:
    """Check a nudge adds its step to the current move, stops at ±300 mm, and lands on the popup's 3 decimals.

    Fails if the step replaces the move, a move goes past ±300 mm, or 0.2 + 0.1 is kept as
    0.30000000000000004. The popup cannot show or keep a move past 300 mm or a fourth decimal,
    so either would put the needle where the popup says it is not.
    """
    from windows.views.nudge_keys import nudged

    assert nudged(current, step) == expected


def select(window: MainWindow, label: str):
    """Select one channel and return the Channels list, which has the keyboard focus after a pick. A helper, not a test."""
    window.channelsmodel.set_selected_channels(label)
    return window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels


def test_alt_arrow_in_the_list_moves_the_selected_channel_and_marks_its_row(channels_window: MainWindow) -> None:
    """Check Alt+Left and Alt+Page Up in the list move the selected channel, underline its row and update its tooltip.

    Fails if the channel does not end at (-1, 0, 1), the row is not underlined, or the tooltip
    does not give the move. A nudged needle that looks untouched hides a change to a patient device.
    """
    label = channel_label(channels_window, 0)
    lister = select(channels_window, label)

    QTest.keyClick(lister, Qt.Key.Key_Left, ALT)
    QTest.keyClick(lister, Qt.Key.Key_PageUp, ALT)

    row = lister.findItems(label, Qt.MatchFlag.MatchExactly)[0]
    assert channels_window.channelsmodel.channels[label].translation == (-1.0, 0.0, 1.0)
    assert row.font().underline()
    assert "Moved by X -1, Y 0, Z 1 mm from the plan" in row.toolTip()
    channels_window.channelsmodel.clear_selected_channels()


def test_a_nudge_adds_to_the_popups_move_and_the_popup_shows_the_total(channels_window: MainWindow) -> None:
    """Check a nudge after a popup move adds to it, and the popup then opens at the total.

    Fails if the nudge replaces the popup's move or the popup opens at another value. Opening
    at a stale value and pressing OK would silently undo the nudge.
    """
    label = channel_label(channels_window, 1)
    double_click_row(channels_window, label, (2.0, 0.0, 0.0))
    lister = select(channels_window, label)

    QTest.keyClick(lister, Qt.Key.Key_Right, ALT | SHIFT)

    assert double_click_row(channels_window, label, None).asked == [(label, (2.1, 0.0, 0.0))]
    channels_window.channelsmodel.clear_selected_channels()


def test_plain_arrows_still_move_through_the_list_and_move_nothing(channels_window: MainWindow) -> None:
    """Check a plain Down in the list selects the next row and moves no channel.

    Fails if the selection stays put or any channel moves. Plain arrows are how a physicist
    walks through the needles, and that must not start moving them.
    """
    model = channels_window.channelsmodel
    before = {name: channel.translation for name, channel in model.channels.items()}
    lister = select(channels_window, channel_label(channels_window, 2))

    QTest.keyClick(lister, Qt.Key.Key_Down)

    assert model.get_selected_channel() == channel_label(channels_window, 3)
    assert {name: channel.translation for name, channel in model.channels.items()} == before
    model.clear_selected_channels()


def test_nothing_moves_with_no_selection_or_for_the_tandem(channels_window: MainWindow) -> None:
    """Check Alt+Right moves nothing when no channel is selected, or when the selected one is the tandem.

    Fails if any channel moves, or if the tandem's nudge reaches move_channel, which raises
    ValueError. The tandem is aimed from its plan path, so a move would be wrong on screen.
    """
    model = channels_window.channelsmodel
    before = {name: channel.translation for name, channel in model.channels.items()}
    lister = channels_window.navigationmodel.views[CHANNELS_TAB].ui.listwidget_channels
    model.clear_selected_channels()

    QTest.keyClick(lister, Qt.Key.Key_Right, ALT)
    label = channel_label(channels_window, 4)
    select(channels_window, label)
    with marked_as_tandem(channels_window, label):
        QTest.keyClick(lister, Qt.Key.Key_Right, ALT)

    assert {name: channel.translation for name, channel in model.channels.items()} == before
    model.clear_selected_channels()


def test_a_nudge_at_the_limit_does_not_rebuild_the_channel(channels_window: MainWindow) -> None:
    """Check Alt+Right at X 300 mm keeps the move and the built shape.

    Fails if the move passes 300 mm, or the shape is rebuilt for a move that changed nothing,
    which takes about 0.6 s and would freeze the window on every press at the limit.
    """
    model = channels_window.channelsmodel
    label = channel_label(channels_window, 5)
    model.move_channel(label, 300.0, 0.0, 0.0)
    built = model.channels[label].shape()
    lister = select(channels_window, label)

    QTest.keyClick(lister, Qt.Key.Key_Right, ALT)

    assert model.channels[label].translation == (300.0, 0.0, 0.0)
    assert model.channels[label].shape() is built
    model.move_channel(label, 0.0, 0.0, 0.0)
    model.clear_selected_channels()


def test_a_nudge_out_of_the_cylinder_warns_in_the_row_tooltip(channels_window: MainWindow) -> None:
    """Check a needle nudged from 99 to 100 mm in X carries the outside-cylinder warning in its tooltip.

    Fails if the tooltip lacks it. The reference sheet drops a needle outside the base circle,
    and the list is where a physicist nudging by eye would see that.
    """
    model = channels_window.channelsmodel
    label = channel_label(channels_window, 6)
    model.move_channel(label, 99.0, 0.0, 0.0)
    lister = select(channels_window, label)

    QTest.keyClick(lister, Qt.Key.Key_Right, ALT)

    row = lister.findItems(label, Qt.MatchFlag.MatchExactly)[0]
    assert model.channels[label].translation == (100.0, 0.0, 0.0)
    assert "outside the base circle of the cylinder" in row.toolTip()
    model.clear_selected_channels()


def test_alt_arrow_in_the_3d_view_moves_the_selected_channel(channels_window: MainWindow) -> None:
    """Check Alt+Down and Alt+Ctrl+Up sent to the 3D view move the selected channel by Y -1 and Z +1.

    Fails if the 3D view ignores the keys. A needle picked by clicking it in the 3D view leaves
    the keyboard focus there, so that is where a physicist lining it up by eye presses the keys.
    """
    model = channels_window.channelsmodel
    label = channel_label(channels_window, 7)
    select(channels_window, label)

    QTest.keyClick(channels_window.canvas, Qt.Key.Key_Down, ALT)
    QTest.keyClick(channels_window.canvas, Qt.Key.Key_Up, ALT | CTRL)

    assert model.channels[label].translation == (0.0, -1.0, 1.0)
    model.clear_selected_channels()


@pytest.mark.parametrize(("key", "modifiers"), [(Qt.Key.Key_A, NONE), (Qt.Key.Key_Left, ALT)])
def test_a_key_the_3d_view_does_not_use_is_passed_on(channels_window: MainWindow, key: Qt.Key, modifiers: Qt.KeyboardModifier) -> None:
    """Check a plain A, and Alt+Left with nothing selected, reach the 3D view and are passed on to its parent.

    Fails if the key event comes back accepted. The 3D view's key handler read a `_key_map` that
    was never created, so every key raised AttributeError there and was swallowed instead of
    reaching the window (section 7.9 of the project docs).
    """
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    channels_window.channelsmodel.clear_selected_channels()
    event = QKeyEvent(QKeyEvent.Type.KeyPress, key, modifiers)

    QApplication.sendEvent(channels_window.canvas, event)

    assert not event.isAccepted()


def send_key(widget, event_type, key: Qt.Key, modifiers: Qt.KeyboardModifier, repeat: bool = False) -> bool:
    """Send one key press or release, marked as a key repeat or not, and return whether it was accepted. A helper, not a test.

    QTest cannot mark a press as a repeat, which is what Qt sends while a key is held down.
    """
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    event = QKeyEvent(event_type, key, modifiers, "", repeat)
    QApplication.sendEvent(widget, event)
    return event.isAccepted()


def test_holding_a_key_moves_once_now_and_once_on_release(channels_window: MainWindow) -> None:
    """Check a held Alt+Right moves 1 mm at once, holds the repeats without rebuilding, and adds them on release.

    Fails if the four repeats rebuild the channel's shape while the key is down, or if the release
    does not leave the move at 5 mm. Each move rebuilds the needle, about 0.6 s, so rebuilding on
    every repeat would queue seconds of work and keep moving the needle after the key is let go.
    """
    from PySide6.QtCore import QEvent

    model = channels_window.channelsmodel
    label = channel_label(channels_window, 8)
    lister = select(channels_window, label)

    send_key(lister, QEvent.Type.KeyPress, Qt.Key.Key_Right, ALT)
    assert model.channels[label].translation == (1.0, 0.0, 0.0)
    built = model.channels[label].shape()
    for _ in range(4):
        assert send_key(lister, QEvent.Type.KeyPress, Qt.Key.Key_Right, ALT, repeat=True)
    assert model.channels[label].shape() is built

    send_key(lister, QEvent.Type.KeyRelease, Qt.Key.Key_Right, ALT)

    assert model.channels[label].translation == (5.0, 0.0, 0.0)
    model.clear_selected_channels()


def test_held_repeats_are_applied_when_the_focus_leaves(channels_window: MainWindow) -> None:
    """Check repeats held back while Alt+Up is down are applied if the list loses the focus before the release.

    Fails if the move stays at the first 1 mm. The release then goes to another widget, and repeats
    left waiting would land on whatever channel is selected at some later release.
    """
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QFocusEvent
    from PySide6.QtWidgets import QApplication

    model = channels_window.channelsmodel
    label = channel_label(channels_window, 9)
    lister = select(channels_window, label)
    send_key(lister, QEvent.Type.KeyPress, Qt.Key.Key_Up, ALT)
    send_key(lister, QEvent.Type.KeyPress, Qt.Key.Key_Up, ALT, repeat=True)
    send_key(lister, QEvent.Type.KeyPress, Qt.Key.Key_Up, ALT, repeat=True)

    QApplication.sendEvent(lister, QFocusEvent(QEvent.Type.FocusOut))

    assert model.channels[label].translation == (0.0, 3.0, 0.0)
    model.move_channel(label, 0.0, 0.0, 0.0)
    model.clear_selected_channels()


def test_a_held_key_with_nothing_selected_is_passed_on(channels_window: MainWindow) -> None:
    """Check repeats of Alt+Left, with no channel selected, are not taken by the nudge.

    Fails if a repeat comes back accepted from the 3D view. Holding a key with nothing selected
    must behave as it did before the nudge existed.
    """
    from PySide6.QtCore import QEvent

    channels_window.channelsmodel.clear_selected_channels()
    canvas = channels_window.canvas

    send_key(canvas, QEvent.Type.KeyPress, Qt.Key.Key_Left, ALT)

    assert not send_key(canvas, QEvent.Type.KeyPress, Qt.Key.Key_Left, ALT, repeat=True)


def pad(window: MainWindow):
    """Return the Channels tab's on-screen nudge pad. A helper, not a test."""
    return window.navigationmodel.views[CHANNELS_TAB].nudge_pad


def test_the_pad_buttons_nudge_the_selected_channel_like_the_keys(channels_window: MainWindow) -> None:
    """Check the pad's right arrow, its Z+ button, and its up arrow with Fine ticked move the selected channel.

    Fails if the channel does not end at (1, 0.1, 1). The pad is the way in for a physicist who
    does not know the keys, so a button that moved the wrong axis would move a patient's needle
    somewhere the arrow on it does not point.
    """
    model = channels_window.channelsmodel
    label = channel_label(channels_window, 10)
    select(channels_window, label)
    buttons = pad(channels_window).buttons

    QTest.mouseClick(buttons[Qt.Key.Key_Right], Qt.MouseButton.LeftButton)
    QTest.mouseClick(buttons[Qt.Key.Key_PageUp], Qt.MouseButton.LeftButton)
    pad(channels_window).fine.setChecked(True)
    QTest.mouseClick(buttons[Qt.Key.Key_Up], Qt.MouseButton.LeftButton)

    assert model.channels[label].translation == (1.0, 0.1, 1.0)
    pad(channels_window).fine.setChecked(False)
    model.move_channel(label, 0.0, 0.0, 0.0)
    model.clear_selected_channels()


def test_the_pad_is_enabled_only_for_a_channel_that_can_be_moved(channels_window: MainWindow) -> None:
    """Check the pad is off with nothing selected, on for a needle, and off for the tandem, like Move....

    Fails if the pad is enabled with no selection or for the tandem, or disabled for a needle.
    A live pad with nothing selected offers a move that goes nowhere, and for the tandem one the
    model must refuse.
    """
    model = channels_window.channelsmodel
    label = channel_label(channels_window, 11)

    model.clear_selected_channels()
    assert not pad(channels_window).isEnabled()
    model.set_selected_channels(label)
    assert pad(channels_window).isEnabled()
    with marked_as_tandem(channels_window, label):
        model.update()
        assert not pad(channels_window).isEnabled()
    model.clear_selected_channels()


def test_every_pad_button_names_its_move_and_key_without_a_colon(channels_window: MainWindow) -> None:
    """Check each pad button's tooltip names its axis and its key, with no colon or em dash.

    Fails if a tooltip lacks the axis or the key, or breaks the UI copy rule in AGENTS.md. The
    tooltip is how a physicist learns the keyboard shortcut from the pad.
    """
    tips = {key: button.toolTip() for key, button in pad(channels_window).buttons.items()}

    assert "X −" in tips[Qt.Key.Key_Left] and "←" in tips[Qt.Key.Key_Left]
    assert "Z +" in tips[Qt.Key.Key_PageUp] and "Page Up" in tips[Qt.Key.Key_PageUp]
    assert all(":" not in tip and "—" not in tip for tip in tips.values())
