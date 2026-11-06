"""Exercise editing an applicator, plan or custom, on the Channels tab: the model rules, the Edit Applicator button and the form."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace
from math import dist
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


@pytest.fixture
def restored_plan(channels_window: MainWindow) -> Iterator[None]:
    """Reload the imported plan after a test that edits a plan applicator. A fixture, not a test.

    The window is shared by every test in this file, so a plan applicator turned into a custom
    one by one test would be different in the next. Loading the plan again rebuilds every plan
    applicator, as a new import does.
    """
    yield
    channels_window.channelsmodel.load_data(channels_window.dicommodel.data)
    channels_window.navigationmodel.views[CHANNELS_TAB].create_channels_list()


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

    new = model.edit_channel("Custom Applicator83", spec("Custom Applicator83", x=-4.0, length2=40.0))

    assert [list(point) for point in new.get_points()] == [[-3.0, 0.0, 80.0], [-3.0, 0.0, 0.0]]
    assert new.channel_number == old.channel_number and new.label == "Custom Applicator83"
    assert list(model.channels).index("Custom Applicator83") == place and model.channels["Custom Applicator83"] is new
    assert "Custom Applicator83" in model.disabled_channels and new.get_diameter() == 4.0 and new.translation == (1.0, 2.0, 0.0)
    assert model.custom_specs["Custom Applicator83"].length2 == 40.0


def test_the_edit_form_for_a_plan_applicator_starts_from_numbers_estimated_from_its_points(channels_window: MainWindow) -> None:
    """Check Applicator6, an imported needle, is offered Ex1's estimated numbers, and a custom one its stored spec.

    Fails if a plan needle is offered defaults or the stored-spec lookup raises KeyError, so the
    clinician would retype every number for a needle the plan already placed, or if a custom one
    is estimated from its points, which loses the bend radius they typed.
    """
    model = channels_window.channelsmodel
    stored = spec("Custom Applicator95")
    model.add_custom_needle(stored)

    estimate = model.spec_for_edit("Applicator6")

    assert (estimate.label, estimate.length1, estimate.theta) == ("Applicator6", pytest.approx(102.82, abs=0.05), pytest.approx(14.59, abs=0.05))
    assert (estimate.x, estimate.y, estimate.length2, estimate.phi) == pytest.approx((5.84, 3.43, 66.12, 29.87), abs=0.05)
    assert model.spec_for_edit("Custom Applicator95") == stored


def test_a_plan_applicator_is_rebuilt_from_the_form_and_keeps_its_number_place_diameter_disabled_state_and_move(
        channels_window: MainWindow, restored_plan: None) -> None:
    """Check editing Applicator6 with a Length 2 5 mm longer keeps everything of it but its path, which is now a custom one.

    Fails if the channel number, list place, own diameter, disabled state or move is lost, if the
    path is not rebuilt, or if the record of the numbers is missing, because the Edit form
    would then offer an estimate again instead of what the clinician typed.
    """
    model = channels_window.channelsmodel
    old = model.channels["Applicator6"]
    model.toggle_channel_enabled("Applicator6")
    model.set_channel_diameter("Applicator6", 4.0)
    model.move_channel("Applicator6", 1.0, 2.0, 0.0)
    place = list(model.channels).index("Applicator6")
    estimate = model.spec_for_edit("Applicator6")

    new = model.edit_channel("Applicator6", replace(estimate, length2=estimate.length2 + 5.0))

    assert new is not old and model.channels["Applicator6"] is new and new.channel_number == old.channel_number
    assert list(model.channels).index("Applicator6") == place and "Applicator6" in model.disabled_channels
    assert new.get_diameter() == 4.0 and new.translation == (1.0, 2.0, 0.0)
    assert model.is_custom_needle("Applicator6") and model.custom_specs["Applicator6"].length2 == pytest.approx(estimate.length2 + 5.0)
    assert dist(new.points_raw[0], old.points_raw[0]) == pytest.approx(5.0, abs=0.5)


def test_pressing_ok_on_the_estimate_alone_leaves_the_tip_of_a_plan_applicator_where_the_plan_put_it(
        channels_window: MainWindow, restored_plan: None) -> None:
    """Check rebuilding Applicator6 from its own estimated numbers puts the new tip within 0.5 mm of the plan's.

    Fails if the estimate and the builder disagree about the frame, the angle or a length, which
    would move the needle's tip by millimetres the moment the clinician pressed OK to change
    only its name. The source stops at the tip, so a moved tip is a moved dose.
    """
    model = channels_window.channelsmodel
    plan_tip = list(model.channels["Applicator6"].points_raw[0])

    new = model.edit_channel("Applicator6", model.spec_for_edit("Applicator6"))

    assert dist(new.points_raw[0], plan_tip) < 0.5


def test_a_plan_applicator_edit_with_bad_numbers_is_refused_and_the_plan_needle_is_left_as_it_was(channels_window: MainWindow) -> None:
    """Check an edit of Applicator7 that starts 50 mm out raises CustomNeedleError and keeps its plan points and no spec.

    Fails if the needle is replaced before the numbers are checked, which would swap a needle the
    plan asked for with one that cannot be cut, or if a spec is recorded for the refused edit, so
    the Remove button would stop asking before it deleted a plan needle.
    """
    model = channels_window.channelsmodel
    old = model.channels["Applicator7"]
    points = [list(point) for point in old.points_raw]

    with pytest.raises(CustomNeedleError, match="base"):
        model.edit_channel("Applicator7", replace(model.spec_for_edit("Applicator7"), x=50.0))

    assert model.channels["Applicator7"] is old and old.points_raw == points and not model.is_custom_needle("Applicator7")


def test_editing_an_unknown_label_raises_key_error_and_changes_nothing(channels_window: MainWindow) -> None:
    """Check editing a label no applicator has raises KeyError and leaves the channels as they were.

    Fails if it passes silently or adds a channel, so a stale list row would seem to be edited
    while the printed device kept its old needle.
    """
    model = channels_window.channelsmodel
    before = dict(model.channels)

    with pytest.raises(KeyError):
        model.edit_channel("No Such Applicator", spec("No Such Applicator"))

    assert model.channels == before


def test_an_edited_plan_applicator_follows_the_cylinder_length_like_any_other_needle(channels_window: MainWindow, restored_plan: None) -> None:
    """Check that after a 5 mm height change the estimate and the edited needle both sit 5 mm higher.

    Fails if the estimate ignores height_offset, so the form shows the plan's old numbers for a
    cylinder that has since grown, or if the edited needle is stored without the offset taken
    out, so it moves twice as far as the others, and the printed channel misses the tissue.
    """
    model = channels_window.channelsmodel
    plan_tip = list(model.channels["Applicator6"].points_raw[0])
    model.update_height_offset(5.0)
    try:
        estimate = model.spec_for_edit("Applicator6")
        new = model.edit_channel("Applicator6", estimate)
        assert estimate.length1 == pytest.approx(107.82, abs=0.05)
        assert dist(new.get_points()[0], [plan_tip[0], plan_tip[1], plan_tip[2] + 5.0]) < 0.5
    finally:
        model.update_height_offset(0.0)


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
        model.edit_channel("Custom Applicator84", spec("Custom Applicator84", x=50.0))

    assert model.channels["Custom Applicator84"] is old
    assert [list(point) for point in old.get_points()] == old_points
    assert model.custom_specs["Custom Applicator84"] == spec("Custom Applicator84")


def test_the_edit_button_is_on_for_any_selected_applicator(channels_window: MainWindow) -> None:
    """Check Edit Applicator is off with nothing selected and on for a plan applicator, a custom one and the tandem.

    Fails if it is off for a plan needle, which leaves no way to change one, off for a custom
    one, off for the tandem, which can be edited though it cannot be removed, or if its style has
    no disabled look, since an off button that looks live gets pressed again and again.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator85"))
    model.clear_selected_channels()
    off_when_none = not view.btn_edit_applicator.isEnabled()
    model.set_selected_channels(next(iter(model.channels)))
    on_for_plan = view.btn_edit_applicator.isEnabled()
    model.set_selected_channels("Custom Applicator85")
    on_for_custom = view.btn_edit_applicator.isEnabled()
    data = channels_window.dicommodel.data
    old_tandem, data.tandem_channel = data.tandem_channel, "Custom Applicator85"
    try:
        view.action_update_settings()
        on_for_tandem = view.btn_edit_applicator.isEnabled()
    finally:
        data.tandem_channel = old_tandem

    assert off_when_none and on_for_plan and on_for_custom and on_for_tandem
    assert ":disabled" in view.btn_edit_applicator.styleSheet()


def test_the_edit_button_on_a_plan_applicator_offers_the_estimate_and_cancel_leaves_the_plan_path_alone(
        channels_window: MainWindow, restored_plan: None) -> None:
    """Check Edit on Applicator6 offers the estimated numbers, Cancel keeps the plan needle and OK replaces it.

    Fails if the form is offered anything but the estimate, if Cancel rebuilds or changes the
    needle, or if OK does not replace it. A Cancel that quietly swapped the plan path for a
    rebuilt one would change a needle the clinician chose to leave alone.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    plan_needle = model.channels["Applicator6"]
    plan_points = [list(point) for point in plan_needle.points_raw]
    model.set_selected_channels("Applicator6")
    cancel = view.ask_edit = StubbedEdit(None)
    QTest.mouseClick(view.btn_edit_applicator, Qt.MouseButton.LeftButton)
    assert cancel.offered == [("Applicator6", model.spec_for_edit("Applicator6"))]
    assert model.channels["Applicator6"] is plan_needle and plan_needle.points_raw == plan_points

    view.ask_edit = StubbedEdit(replace(model.spec_for_edit("Applicator6"), length2=70.0))
    QTest.mouseClick(view.btn_edit_applicator, Qt.MouseButton.LeftButton)

    assert model.channels["Applicator6"] is not plan_needle and model.is_custom_needle("Applicator6")


def test_only_an_imported_applicator_gets_the_note_that_ok_replaces_its_plan_path(channels_window: MainWindow) -> None:
    """Check the form's note is shown for a plan applicator, naming Cancel, and is empty for a custom one.

    Fails if the note is missing for a plan needle, so the clinician presses OK without knowing it
    discards the plan's own path, or shown for a custom one, where nothing is replaced and the
    warning teaches them to ignore it. The text must also have no colon or em dash.
    """
    from windows.views.add_applicator_dialog import AddApplicatorDialog

    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator96"))

    plan_note, custom_note = view.edit_note("Applicator6"), view.edit_note("Custom Applicator96")
    with_note = AddApplicatorDialog("a", model.custom_needle_error, spec("a"), plan_note)
    without_note = AddApplicatorDialog("a", model.custom_needle_error, spec("a"))

    assert "replaces the plan path" in plan_note and "Cancel" in plan_note and ":" not in plan_note and "—" not in plan_note
    assert custom_note == "" and with_note.label_note.text() == plan_note
    assert not with_note.label_note.isHidden() and without_note.label_note.isHidden()


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


def test_the_form_opened_to_edit_shows_the_stored_numbers_and_lets_the_name_change(channels_window: MainWindow) -> None:
    """Check the form built from a bent spec shows each number, an editable name and the title Edit Applicator.

    Fails if a field shows its default instead of the stored value, or the name is locked. A
    locked name leaves a wrongly named applicator with no fix except deleting it, and the name
    is what the list, the Tandem tab and the sheet show the clinician.
    """
    from windows.views.add_applicator_dialog import AddApplicatorDialog

    bent = CustomNeedleSpec(label="Custom Applicator88", x=4.0, y=-6.0, length1=30.0, length2=12.5, radius=8.0, theta=45.0, phi=90.0)

    dialog = AddApplicatorDialog(bent.label, channels_window.channelsmodel.custom_needle_error, bent)

    assert dialog.spec() == bent
    assert dialog.edit_label.isEnabled() and dialog.windowTitle() == "Edit Applicator"


def test_renaming_moves_the_label_through_every_record_and_keeps_the_rest(channels_window: MainWindow) -> None:
    """Check an edit that renames a disabled, moved, selected applicator with its own diameter keeps all of that under the new name.

    Fails if the old label stays in channels, custom_specs, own_diameters, disabled_channels,
    selected_channels or the display model's shapes, if the new one is missing from any, if the
    list place or channel number changes, or if the needle still carries its old label. A label
    left behind would be a ghost row, a needle that is no longer disabled and cut, or a viewport
    needle with no channel behind it.
    """
    model = channels_window.channelsmodel
    old = model.add_custom_needle(spec("Custom Applicator91"))
    model.toggle_channel_enabled("Custom Applicator91")
    model.set_channel_diameter("Custom Applicator91", 4.0)
    model.move_channel("Custom Applicator91", 1.0, 2.0, 0.0)
    model.set_selected_channels("Custom Applicator91")
    place = list(model.channels).index("Custom Applicator91")

    new = model.edit_channel("Custom Applicator91", spec("  Renamed Needle  ", x=-4.0))

    assert "Custom Applicator91" not in model.channels and "Custom Applicator91" not in model.custom_specs
    assert "Custom Applicator91" not in model.own_diameters and "Custom Applicator91" not in model.disabled_channels
    assert "Custom Applicator91" not in model.selected_channels and "Custom Applicator91" not in channels_window.displaymodel.shapes
    assert list(model.channels).index("Renamed Needle") == place and model.channels["Renamed Needle"] is new
    assert new.label == "Renamed Needle" and new.channel_number == old.channel_number and new.translation == (1.0, 2.0, 0.0)
    assert model.custom_specs["Renamed Needle"].label == "Renamed Needle" and new.get_diameter() == 4.0
    assert "Renamed Needle" in model.disabled_channels and model.selected_channels == ["Renamed Needle"]


def test_a_rename_to_an_existing_or_blank_name_is_refused_and_nothing_changes(channels_window: MainWindow) -> None:
    """Check renaming to a plan applicator's name or to blank text raises CustomNeedleError and keeps the old name.

    Fails if it is accepted, because two channels cannot share a label. The second would replace
    the first in the dict, silently deleting an applicator from the printed device, and a blank
    label cannot be told apart in the list or on the sheet.
    """
    model = channels_window.channelsmodel
    old = model.add_custom_needle(spec("Custom Applicator92"))
    plan_label = next(iter(model.channels))
    before = dict(model.channels)

    with pytest.raises(CustomNeedleError, match="already exists"):
        model.edit_channel("Custom Applicator92", spec(plan_label))
    with pytest.raises(CustomNeedleError, match="Name"):
        model.edit_channel("Custom Applicator92", spec("   "))

    assert model.channels == before and model.channels["Custom Applicator92"] is old


def test_renaming_the_tandem_keeps_the_tandem_tab_pointing_at_it(channels_window: MainWindow) -> None:
    """Check renaming the applicator that is the tandem moves data.tandem_channel and the Tandem tab's choice with it.

    Fails if tandem_channel keeps the old label, because get_tandem_channel then raises
    KeyError, which stops the Tandem tab and the export, or if the Tandem tab's box no longer
    shows the renamed channel as chosen, so the clinician would think no tandem is set.
    """
    model = channels_window.channelsmodel
    data = channels_window.dicommodel.data
    tandem_box = channels_window.navigationmodel.views[3].ui.cb_tandem_channel
    model.add_custom_needle(spec("Custom Applicator93"))
    old_tandem, data.tandem_channel = data.tandem_channel, "Custom Applicator93"
    try:
        new = model.edit_channel("Custom Applicator93", spec("Renamed Tandem"))

        assert data.tandem_channel == "Renamed Tandem" and model.get_tandem_channel() is new
        assert tandem_box.currentData() == "Renamed Tandem"
    finally:
        data.tandem_channel = old_tandem


def test_the_edit_button_with_a_new_name_renames_the_list_row(channels_window: MainWindow) -> None:
    """Check pressing Edit Applicator and answering with a new name shows that name in the list and keeps it selected.

    Fails if the row keeps the old name or the selection is lost, because the Disable, Move and
    Remove buttons then act on nothing and the clinician cannot tell which row was edited.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    model.add_custom_needle(spec("Custom Applicator94"))
    view.create_channels_list()
    model.set_selected_channels("Custom Applicator94")
    view.ask_edit = StubbedEdit(spec("Renamed Row"))

    QTest.mouseClick(view.btn_edit_applicator, Qt.MouseButton.LeftButton)

    assert view.ui.listwidget_channels.findItems("Renamed Row", Qt.MatchFlag.MatchExactly)
    assert not view.ui.listwidget_channels.findItems("Custom Applicator94", Qt.MatchFlag.MatchExactly)
    assert model.get_selected_channel() == "Renamed Row"
