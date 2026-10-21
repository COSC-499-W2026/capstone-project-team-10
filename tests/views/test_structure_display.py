"""Anatomy preview state and its Import controls without a native canvas."""
from pathlib import Path
import pytest
from classes.dicom.data import DicomData
from classes.dicom.structures import Contour, Structure, StructureType


@pytest.fixture
def anatomy_model(units_app):
    """Build an isolated anatomy model with a closed organ and a reference axis.

    Import errors fail this helper; literal coordinates allow bounds checks to catch
    misplaced anatomy without relying on the production transform for expectations.
    """
    from windows.models.structures_model import StructuresModel
    model = StructuresModel()
    plan = DicomData()
    plan.cylinder_base = (0., 0., 0.)
    plan.cylinder_direction = (0., 0., 10.)
    plan.central_channel_roi = 1
    plan.structures = (
        Structure(1, 'Axis', 'frame', (255, 255, 255), None, StructureType.OTHER, ()),
        Structure(2, 'Organ', 'frame', (0, 255, 0), 'ORGAN', StructureType.ORGAN,
                  (Contour('CLOSED_PLANAR', ((0., 0., 5.), (2., 0., 5.), (0., 2., 5.))),)),
        Structure(3, 'Wrong frame', 'different', (255, 0, 0), 'ORGAN', StructureType.ORGAN,
                  (Contour('CLOSED_PLANAR', ((0., 0., 5.), (2., 0., 5.), (0., 2., 5.))),)),
    )
    model.load_plan(plan, 20.)
    return model


def test_organs_show_by_default_but_unregistered_geometry_is_unavailable(anatomy_model):
    """Show valid organs and refuse anatomy from another patient frame.

    Missing preview or inclusion of ROI 3 fails; mismatched anatomy could otherwise
    imply a false relationship between a needle and an organ.
    """
    assert anatomy_model.visible == {2}
    assert len(anatomy_model.presentations()) == 1
    assert 'frame' in anatomy_model.unavailable[3].lower()
    with pytest.raises(ValueError):
        anatomy_model.set_visible(3, True)


def test_anatomy_length_change_and_hide_preserve_geometry(anatomy_model):
    """Shift the anatomy with the needle tip and allow reversible visibility.

    Wrong Z bounds or lost visibility fails and would misalign the contour preview
    after changing cylinder length.
    """
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib
    anatomy_model.set_length(30.)
    bounds = Bnd_Box()
    brepbndlib.AddOptimal(anatomy_model.presentations()[0].outline, bounds)
    assert bounds.Get()[2] == pytest.approx(25., abs=1e-6)
    anatomy_model.set_visible(2, False)
    assert anatomy_model.presentations() == ()
    anatomy_model.set_visible(2, True)
    assert len(anatomy_model.presentations()) == 1
    anatomy_model.clear()
    assert anatomy_model.presentations() == ()
    assert anatomy_model.structures == {}


def test_import_list_checkboxes_control_anatomy_and_failed_import_clears_it(channels_window, tmp_path: Path):
    """Use real Import checkboxes and verify a failed new import clears old anatomy.

    A missing checkbox update or remaining preview after failure fails; the previous
    patient's contours must not survive an import attempt.
    """
    from PySide6.QtCore import Qt
    view = channels_window.navigationmodel.views[0]
    model = channels_window.structuresmodel
    view.action_update_structure_list()
    item = view.structure_list.item(0)
    roi = item.data(Qt.UserRole)
    assert roi == 1
    item.setCheckState(Qt.Checked)
    assert roi in model.visible
    assert model.presentations()
    view.structure_list.item(0).setCheckState(Qt.Unchecked)
    assert roi not in model.visible
    assert all(not label.startswith('structure:') for label in channels_window.displaymodel.shapes)
    view.import_dicom_from_folder(str(tmp_path))
    assert not model.structures
    assert not model.presentations()
