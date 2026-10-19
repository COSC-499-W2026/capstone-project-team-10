"""Exercise the needle template controls in the Channels tab's Selected Channel group."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from test_channels_view import CHANNELS_TAB, click, open_channels_tab_and_select

if TYPE_CHECKING:
    from windows.main_window import MainWindow

TEMPLATE_SOURCE_CHANNEL = "Applicator9"
TEMPLATE_TARGET_CHANNEL = "Applicator10"


def library_path() -> Path:
    """Return the needle template library inside this run's temporary home folder.

    A helper, not a test. units_app points HOME at a temporary folder before brachify is
    imported, so this never touches the developer's own ~/brachify.
    """
    from classes.info import USER_PATH
    from settings.needle_templates import LIBRARY_FILE_NAME

    return USER_PATH / LIBRARY_FILE_NAME


def save_template_from(window: MainWindow, label: str, name: str, diameter: float) -> None:
    """Select a channel, type a diameter and a name, and press Save as Template.

    A helper, not a test. It drives the real controls in the order a clinician uses them.
    """
    view = window.navigationmodel.views[CHANNELS_TAB]
    open_channels_tab_and_select(window, label)
    view.ui.sb_channel_diameter.setValue(diameter)
    view.ui.le_template_name.setText(name)
    click(view.ui.btn_save_template)


def test_a_saved_template_is_listed_and_written_to_the_library(channels_window: MainWindow) -> None:
    """Check that Save as Template adds the template to the list and to the library file.

    Fails if "Plastic test  2.400 mm" is not offered in the template list, or the file does
    not hold it. A template that is only listed is lost when brachify closes, and FR-CN-05
    asks for one the clinician can use later.
    """
    from settings.needle_templates import NeedleTemplate, load_templates

    save_template_from(channels_window, TEMPLATE_SOURCE_CHANNEL, "Plastic test", 2.4)
    view = channels_window.navigationmodel.views[CHANNELS_TAB]

    assert view.ui.cb_needle_templates.findText("Plastic test  2.400 mm") >= 0
    assert NeedleTemplate("Plastic test", 2.4) in load_templates(library_path())


def test_applying_a_template_gives_the_selected_channel_its_diameter(channels_window: MainWindow) -> None:
    """Check that Apply Template sets the selected channel's own diameter to the template's.

    "Metal test" is saved from Applicator9 at 1.9 mm, then applied to Applicator10. Fails if
    Applicator10 is not 1.9 mm with an own diameter. That is the card's last step, the
    applicator using the saved needle template.
    """
    save_template_from(channels_window, TEMPLATE_SOURCE_CHANNEL, "Metal test", 1.9)
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    model = channels_window.channelsmodel
    open_channels_tab_and_select(channels_window, TEMPLATE_TARGET_CHANNEL)

    view.ui.cb_needle_templates.setCurrentIndex(view.ui.cb_needle_templates.findText("Metal test  1.900 mm"))
    click(view.ui.btn_apply_template)

    assert model.channels[TEMPLATE_TARGET_CHANNEL].get_diameter() == 1.9
    assert model.has_own_diameter(TEMPLATE_TARGET_CHANNEL)


def test_saving_a_template_without_a_name_says_why_and_saves_nothing(channels_window: MainWindow) -> None:
    """Check that a blank name shows the reason beside the controls and adds no template.

    Fails if the template list grows, or the status line does not say a name is needed. This
    is FR-CN-05's negative case. A silent refusal would leave the clinician unsure whether the
    template was saved.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    listed_before = view.ui.cb_needle_templates.count()

    save_template_from(channels_window, TEMPLATE_SOURCE_CHANNEL, "   ", 2.2)

    assert view.ui.cb_needle_templates.count() == listed_before
    assert view.ui.label_template_status.text() == "A needle template needs a name"


def test_an_unreadable_library_is_reported_and_leaves_the_tab_usable(channels_window: MainWindow) -> None:
    """Check that a corrupt library file empties the list, names the file, and raises nothing.

    Fails if loading raises, or the list still offers templates, or Apply Template stays
    enabled. The library is read when the window is built, so an exception here would stop
    brachify from starting, and startup failures only reach app.log. The file is removed
    afterwards, so later tests start from an empty library.
    """
    view = channels_window.navigationmodel.views[CHANNELS_TAB]
    library = library_path()
    library.parent.mkdir(parents=True, exist_ok=True)
    library.write_text("not json", encoding="utf-8")
    try:
        view.action_load_templates()

        assert view.ui.cb_needle_templates.count() == 0
        assert not view.ui.btn_apply_template.isEnabled()
        assert library.name in view.ui.label_template_status.text()
    finally:
        library.unlink()
        view.action_load_templates()
