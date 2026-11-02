"""Exercise editing a custom applicator on the Channels tab: the model rules, the Edit Applicator button and the form."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from classes.mesh.helper import CustomNeedleError, CustomNeedleSpec

if TYPE_CHECKING:
    from windows.main_window import MainWindow

CHANNELS_TAB = 2


def spec(label: str, x: float = 3.0, length2: float = 25.0) -> CustomNeedleSpec:
    """Make a straight spec at (x, -2) with Length 1 of 40 and the given Length 2. A helper, not a test."""
    return CustomNeedleSpec(label=label, x=x, y=-2.0, length1=40.0, length2=length2)


class StubbedEdit:
    """Stand in for the Edit Applicator form, as a helper and not a test.

    Assigned to ChannelsView.ask_edit, the view's seam for that form, so no module is patched.
    It records the label and spec the view offered and gives the chosen answer, None meaning Cancel.
    """

    def __init__(self, answer: CustomNeedleSpec | None) -> None:
        """Remember the answer to give, None meaning Cancel. A helper, not a test."""
        self.answer = answer
        self.offered: list[tuple[str, CustomNeedleSpec]] = []

    def __call__(self, label: str, current: CustomNeedleSpec) -> CustomNeedleSpec | None:
        """Record what the view offered and return the chosen answer. A helper, not a test."""
        self.offered.append((label, current))
        return self.answer


def test_editing_rebuilds_the_needle_but_keeps_its_name_number_place_diameter_and_disabled_state(channels_window: MainWindow) -> None:
    """Check an edit to x -4 and Length 2 of 40 moves the tip from 65 to 80 and keeps everything else of the applicator.

    Fails if the points stay as they were, the channel number or list place changes, or the own
    diameter, disabled state or move is lost. The sheet lists needles by channel number, so a
    number that changed on edit would send the clinician to the wrong hole, and a lost move
    would put the needle back where the clinician had moved it away from.
    """
    model = channels_window.channelsmodel
    old = model.add_custom_needle(spec("Custom Applicator83"))
    model.toggle_channel_enabled("Custom Applicator83")
    model.set_channel_diameter("Custom Applicator83", 4.0)
    model.move_channel("Custom Applicator83", 1.0, 2.0, 0.0)
    place = list(model.channels).index("Custom Applicator83")

    new = model.edit_custom_needle("Custom Applicator83", spec("Custom Applicator83", x=-4.0, length2=40.0))

    assert [list(point) for point in new.get_points()] == [[-3.0, 0.0, 80.0], [-3.0, 0.0, 0.0]]
    assert new.channel_number == old.channel_number and new.label == "Custom Applicator83"
    assert list(model.channels).index("Custom Applicator83") == place and model.channels["Custom Applicator83"] is new
    assert "Custom Applicator83" in model.disabled_channels and new.get_diameter() == 4.0 and new.translation == (1.0, 2.0, 0.0)
    assert model.custom_specs["Custom Applicator83"].length2 == 40.0


def test_a_plan_applicator_cannot_be_edited_and_nothing_changes(channels_window: MainWindow) -> None:
    """Check editing an imported applicator raises CustomNeedleError and leaves the channels as they were.

    Fails if it is accepted. The imported needles come from the treatment plan, so rebuilding
    one from typed numbers would replace a needle the plan asked for with one it never had.
    """
    model = channels_window.channelsmodel
    label = next(iter(model.channels))
    before = dict(model.channels)

    with pytest.raises(CustomNeedleError, match="custom"):
        model.edit_custom_needle(label, spec(label))

    assert model.channels == before


def test_an_edit_with_bad_numbers_is_refused_and_the_needle_is_left_as_it_was(channels_window: MainWindow) -> None:
    """Check an edit that starts 50 mm from the centre raises CustomNeedleError and keeps the old points and spec.

    Fails if the model changes the needle before it has checked the numbers, which leaves a
    needle whose stored spec and drawn shape disagree, so the form would later show numbers
    that the printed channel does not have.
    """
    model = channels_window.channelsmodel
    old = model.add_custom_needle(spec("Custom Applicator84"))
    old_points = [list(point) for point in old.get_points()]

    with pytest.raises(CustomNeedleError, match="base"):
        model.edit_custom_needle("Custom Applicator84", spec("Custom Applicator84", x=50.0))

    assert model.channels["Custom Applicator84"] is old
    assert [list(point) for point in old.get_points()] == old_points
    assert model.custom_specs["Custom Applicator84"] == spec("Custom Applicator84")


def test_the_edit_button_is_on_only_for_a_selected_custom_applicator(channels_window: MainWindow) -> None:
    """Check Edit Applicator is off with nothing or a plan applicator selected and on for a custom one, tandem or not.

    Fails if it is on for a plan needle, which invites rebuilding one the plan asked for, off
    for a custom one, which leaves no way to change it, off for a custom tandem, which can be
    edited though it cannot be removed, or if its style has no disabled look, since an off
    button that looks live gets pressed again and again.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator85"))
    model.clear_selected_channels()
    off_when_none = not view.btn_edit_applicator.isEnabled()
    model.set_selected_channels(next(iter(model.channels)))
    off_for_plan = not view.btn_edit_applicator.isEnabled()
    model.set_selected_channels("Custom Applicator85")
    on_for_custom = view.btn_edit_applicator.isEnabled()
    data = channels_window.dicommodel.data
    old_tandem, data.tandem_channel = data.tandem_channel, "Custom Applicator85"
    try:
        view.action_update_settings()
        on_for_tandem = view.btn_edit_applicator.isEnabled()
    finally:
        data.tandem_channel = old_tandem

    assert off_when_none and off_for_plan and on_for_custom and on_for_tandem
    assert ":disabled" in view.btn_edit_applicator.styleSheet()


def test_the_edit_button_offers_the_current_numbers_applies_the_answer_and_cancel_changes_nothing(channels_window: MainWindow) -> None:
    """Check Edit Applicator offers the stored spec, Cancel keeps the needle and an answer rebuilds it.

    Fails if the form is not given the current numbers, which makes the clinician retype every
    one, if Cancel changes the needle, or if the answer is not applied to the model.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    channel = model.add_custom_needle(spec("Custom Applicator87"))
    model.set_selected_channels("Custom Applicator87")
    cancel = view.ask_edit = StubbedEdit(None)
    QTest.mouseClick(view.btn_edit_applicator, Qt.MouseButton.LeftButton)
    assert cancel.offered == [("Custom Applicator87", spec("Custom Applicator87"))] and model.channels["Custom Applicator87"] is channel

    view.ask_edit = StubbedEdit(spec("Custom Applicator87", length2=30.0))
    QTest.mouseClick(view.btn_edit_applicator, Qt.MouseButton.LeftButton)

    assert model.channels["Custom Applicator87"].get_points()[0][2] == 70.0


def test_the_form_opened_to_edit_shows_the_stored_numbers_with_the_name_locked(channels_window: MainWindow) -> None:
    """Check the form built from a bent spec shows each number, a locked name and the title Edit Applicator.

    Fails if a field shows its default instead of the stored value, or the name can be typed
    over. The needle's name is its identity in the list, the disabled set and the own
    diameters, so a renamed needle would lose its state.
    """
    from windows.views.add_applicator_dialog import AddApplicatorDialog

    bent = CustomNeedleSpec(label="Custom Applicator88", x=4.0, y=-6.0, length1=30.0, length2=12.5, radius=8.0, theta=45.0, phi=90.0)

    dialog = AddApplicatorDialog(bent.label, channels_window.channelsmodel.custom_needle_error, bent)

    assert dialog.spec() == bent
    assert not dialog.edit_label.isEnabled() and dialog.windowTitle() == "Edit Applicator"
