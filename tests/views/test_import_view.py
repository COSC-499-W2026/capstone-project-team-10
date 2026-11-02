"""Tests for the Import tab's structure list after a DICOM import."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from windows.main_window import MainWindow

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PLAN = REPO_ROOT / "SI_C_D30 Brachify_Ex1"
IMPORT_TAB = 0


def test_importing_ex1_fills_the_structure_list(channels_window: MainWindow) -> None:
    """Check that importing Ex1 puts each decoded structure into the Import list.

    Calls import_dicom_from_folder, the path after the folder dialog, with Ex1.
    Fails if that path never calls action_update_structure_list (0 rows), or if
    the first row is not BODY with its category. Without this, DicomData can hold
    structures while the clinician sees an empty Import list (issue #41).
    """
    import_view = channels_window.navigationmodel.views[IMPORT_TAB]
    import_view.structure_list.clear()

    import_view.import_dicom_from_folder(str(SAMPLE_PLAN))

    assert import_view.structure_list.count() == 42
    assert import_view.structure_list.item(0).text() == "BODY  other"


def test_empty_folder_import_clears_the_structure_list(
    channels_window: MainWindow,
    tmp_path: Path,
) -> None:
    """Check that a failed import leaves the structure list empty.

    Fills the list from the already-loaded Ex1 plan, then imports an empty
    folder through the same no-dialog path. Fails if the previous plan's 42
    rows stay visible after the failed import, which would show the wrong anatomy.
    """
    import_view = channels_window.navigationmodel.views[IMPORT_TAB]
    import_view.action_update_structure_list()
    assert import_view.structure_list.count() == 42

    empty = tmp_path / "empty-plan"
    empty.mkdir()
    import_view.import_dicom_from_folder(str(empty))

    assert import_view.structure_list.count() == 0


def test_importing_a_plan_clears_the_previous_plans_tandem(cylinder_window: MainWindow) -> None:
    """Check that importing Ex1 after a tandem was generated for Ex2 leaves no tandem and the default rotation.

    Ex2 is imported, a tandem is generated, then Ex1 is imported, all through the Import tab's
    no-dialog path. Fails if the tandem still exists, if its rotation is not the default 0 degrees,
    or if the plan rotation the warning compares against, or the flag that the plan has a tandem,
    is left over from Ex2. Ex1 has no tandem, so a leftover would cut Ex2's tandem hole into the
    next patient's cylinder without anyone asking for it.
    """
    import_view = cylinder_window.navigationmodel.views[IMPORT_TAB]
    tandem = cylinder_window.tandemmodel
    import_view.import_dicom_from_folder(str(REPO_ROOT / "SI_C_D30 Brachify_Ex2"))
    tandem.tandem_length = 150.0
    tandem.set_tandem()
    tandem.change_tandem_rotation(64.0)
    assert tandem.exists()

    import_view.import_dicom_from_folder(str(SAMPLE_PLAN))

    assert not tandem.exists()
    assert tandem.rotation == 0.0
    assert tandem.protation == 0.0
    assert not tandem.hasTandemInDICOM
