from collections.abc import Callable
from pathlib import Path

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Shape

from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox

from classes.app import get_app
from classes.logger import log
from classes.mesh.fileio import write_3d_file
import classes.pdf.template_reference as template_reference
from windows.models.shape_model import ShapeTypes, ShapeModel
from windows.ui.export_view_ui import Ui_Export_View
from windows.views.custom_view import display_action, CustomView
from windows.views.channels_view import ChannelsView

import json
from settings.reset import getCurrentValues

EXPORT_LABEL = "export"
BASEMAP = "basemap.png"

materials = {
    ShapeTypes.CYLINDER: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.CHANNEL: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.TANDEM: {"rgb": [0.45, 0.45, 0.45], "transparent": True},
    ShapeTypes.SELECTED: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.EXPORT: {"rgb": [0.2, 0.55, 0.55], "transparent": True}
}


def missing_tandem_hole_text(tandem_channel: str | None, has_tandem_hole: bool) -> str:
    """The Export tab's warning for a tandem channel with no tandem hole, or nothing."""
    if tandem_channel is None or has_tandem_hole: return ""
    return (f"{tandem_channel} is the tandem channel, but no tandem has been generated or imported, "
            "so this cylinder has no tandem hole.")


class Export_View(CustomView):

    def tandem_hole_warning(self) -> str:
        return missing_tandem_hole_text(self.window.dicommodel.data.tandem_channel,
                                        self.window.tandemmodel.shape() is not None)

    def show_tandem_hole_warning(self) -> None:
        text = self.tandem_hole_warning()
        self.ui.label_tandem_hole_warning.setText(text)
        self.ui.label_tandem_hole_warning.setHidden(not text)

    def export_allowed(self) -> bool:
        """Ask before exporting a cylinder whose tandem channel has no tandem hole."""
        text = self.tandem_hole_warning()
        return not text or self.confirm_export(text)

    def ask_export(self, text: str) -> bool:
        """The dialog export_allowed asks with. Cancel is the default, so pressing Return exports nothing."""
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("No Tandem Hole")
        dialog.setText(f"{text} Export anyway?")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        return dialog.exec() == QMessageBox.StandardButton.Yes

    def action_export_config(self):
        """
        Create a config.json file to save the current settings as defaults.
        """
        # User chooses location of config file and file name.
        # if user presses "cancel", then returns empty string ("")
        filename = QFileDialog.getSaveFileName(
            self, "Save config", "", "JSON File (*.json)", "")[0]
        
        if not filename:   # no file selected
            log.info("no valid filename selected for config file.")
            return
        
        log.info(f"file {filename} has been selected for exporting config.")

        config_values = getCurrentValues()

        # Save dictionary as .json file
        with open(filename, "w") as outfile:
            json.dump(config_values, outfile, indent=0)

        # save the file path to the most recently saved config file.
        app = get_app()
        # the following value will be saved in filepaths.json, but is not used otherwise. (future developement)
        app.values.most_recently_saved_config_file = filename

        log.info("Successfully saved all the current values.")
        

    def action_export_mesh(self):
        """
        Create a single mesh from boolean subtracting the channels and tandem from the cylinder
        """
        if not self.export_allowed(): return
        filename = QFileDialog.getSaveFileName(
            self, "Save model", "", "STL File (*.stl);; BRep file (*.step *.stp);; All files (*.*))", "")

        if not filename:  # no file selected?
            log.info("no valid filename selected for importing")
            return

        log.info(f"file {filename} has been selected for exporting")
        write_3d_file(filename[0], self.shape)

    def action_export_shapes(self):
        """
        Collect the shapes and export them in a single file
        """
        if not self.export_allowed(): return
        filename = QFileDialog.getSaveFileName(
            self, "Save model", "", "BRep file (*.step *.stp);;", "")

        if not filename:  # no file selected?
            log.info("no valid filename selected for importing")
            return

        log.info(f"file {filename} has been selected for exporting")
        compound = self._final_shape()
        write_3d_file(filename[0], compound)

    def action_export_template_reference(self):
        if not self.export_allowed(): return
        filename = QFileDialog.getSaveFileName(
            self, 'Save solid as PDF', '', "PDF files (*.pdf)")
        
        # error checking
        if not filename[0]:  # no file selected
            log.info("no valid filename selected for importing")
            return
        
        window = get_app().window

        needle_length = get_app().values.config_values.get("CONFIG_DEADSPACE")

        # generate pdf
        tandembool = window.tandemmodel.shape() != None
        # tandem rotation (to show dotted line in image)
        tandem_rotation = window.tandemmodel.rotation
        is_tandem_imported = window.tandemmodel.is_shape_imported

        # colett preview (to show dotted line in Reference Sheet)
        Include_colett_preview = self.ui.cb_collet_preview_reference_sheet.isChecked()

        self.action_apply_collet_settings()  # ensure config values are up to date

        try:
            template_reference.generate_pdf(
                dicom=window.dicommodel.data,
                cylinder=window.cylindermodel.cylinder,
                channels=window.channelsmodel.get_visible_channels(),
                filepath=Path(filename[0]),
                needle_length=needle_length, 
                has_tandem = tandembool,
                tandem_rotation=tandem_rotation, 
                is_tandem_imported=is_tandem_imported,
                include_collet_preview=Include_colett_preview)
        except:
            log.error("PDF did not save")
            get_app().window.pdf_save_error()

    def action_show_tandem(self, tandem_visible: bool):
        self.update_display()

    def on_close(self):
        log.debug(f"on close")

    # don't use @display_action because we want a unique view
    def on_open(self):

        log.debug(f"on open")

        # Ensure Export UI reflects stored config values (important after DICOM import)
        self.load_collet_settings_into_ui()

        # if tandem exists
        if self.window.tandemmodel.shape():
            self.ui.cb_tandem_shown.setEnabled(True)
        else:
            self.ui.cb_tandem_shown.setDisabled(True)

        self.shape = self._final_mesh()
        self.show_tandem_hole_warning()

        self.update_display()

    def update_display(self, *args):
        # export shape
        export_shape = ShapeModel(
            label=EXPORT_LABEL,
            shape=self.shape,
            shape_type=ShapeTypes.EXPORT
        )
        export_shape.material=materials[ShapeTypes.EXPORT]
        shapes = [export_shape]

        # tandem shape
        if self.ui.cb_tandem_shown.isChecked():
            tandemmodel = self.window.tandemmodel
            tandem = tandemmodel.raw_shape()
            if tandem:
                tandem_shape = ShapeModel(
                    label=tandemmodel.get_label(),
                    shape=tandem,
                    shape_type=ShapeTypes.TANDEM
                ) 
                tandem_shape.material = materials[ShapeTypes.TANDEM]
                shapes.append(tandem_shape)
        
        self.window.displaymodel.show_shapes(shapes)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Export_View()
        self.ui.setupUi(self)
        self.window = get_app().window
        self.shape = None  # the model to export
        # the missing tandem hole question asks through this, so a test can answer for the clinician
        self.confirm_export: Callable[[str], bool] = self.ask_export
        self.ui.label_tandem_hole_warning.setHidden(True)

        # signals and slots
        self.ui.btn_export_mesh.pressed.connect(self.action_export_mesh) # when "export mesh" button pressed, then call action_export_mesh function
        self.ui.btn_export_shapes.pressed.connect(self.action_export_shapes)
        self.ui.btn_export_current_config.pressed.connect(self.action_export_config)

        self.ui.btn_export_template_reference.pressed.connect(self.action_export_template_reference)
        
        self.ui.cb_tandem_shown.stateChanged.connect(self.action_show_tandem)

        # Collet spinboxes should persist by updating config_values whenever edited
        self.ui.sb_needle_collet_od.valueChanged.connect(self.action_apply_collet_settings)
        self.ui.sb_tandem_collet_outer_od.valueChanged.connect(self.action_apply_collet_settings)
        self.ui.sb_tandem_collet_inner_od.valueChanged.connect(self.action_apply_collet_settings)

    def _final_mesh(self) -> TopoDS_Shape:
        shape = self.window.cylindermodel.cylinder.shape()

        tandem_shape = self.window.tandemmodel.shape()
        if tandem_shape: shape = BRepAlgoAPI_Cut(shape, tandem_shape).Shape()

        for channel in self.window.channelsmodel.get_visible_channels():
            shape = BRepAlgoAPI_Cut(shape, channel.shape()).Shape()
        
        return shape

    def _final_shape(self) -> TopoDS_Compound:
        compound = TopoDS_Compound()  # houses all the shapes
        shape_tool = BRep_Builder()  # add shapes to the compound
        shape_tool.MakeCompound(compound)

        shape_tool.Add(compound, self.window.cylindermodel.cylinder.shape())

        tandem_shape = self.window.tandemmodel.shape()
        if tandem_shape: shape_tool.Add(compound, self.window.tandemmodel.shape())

        # place all channels in a sub compound
        channels_compound = TopoDS_Compound()
        channel_tool = BRep_Builder()
        channel_tool.MakeCompound(channels_compound)
        for channel in self.window.channelsmodel.get_visible_channels():
            channel_tool.Add(channels_compound, channel.shape())

        shape_tool.Add(compound, channels_compound)
        return compound
    
    def action_apply_collet_settings(self, *args):
        """Push Export UI -> app.values.config_values (like other views do with Apply Settings)."""
        config = get_app().values.config_values
        config["CONFIG_NEEDLE_COLLET_OUTER_DIAMETER"] = self.ui.sb_needle_collet_od.value()
        config["CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER"] = self.ui.sb_tandem_collet_outer_od.value()
        config["CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER"] = self.ui.sb_tandem_collet_inner_od.value()

    def load_collet_settings_into_ui(self):
        """Pull app.values.config_values -> Export UI (like resetAllValues does for other views)."""
        config = get_app().values.config_values

        needle_od = config.get("CONFIG_NEEDLE_COLLET_OUTER_DIAMETER")
        tandem_outer = config.get("CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER")
        tandem_inner = config.get("CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER")

        # Avoid triggering valueChanged -> apply while loading
        self.ui.sb_needle_collet_od.blockSignals(True)
        self.ui.sb_tandem_collet_outer_od.blockSignals(True)
        self.ui.sb_tandem_collet_inner_od.blockSignals(True)

        try:
            if needle_od is not None:
                self.ui.sb_needle_collet_od.setValue(float(needle_od))
            if tandem_outer is not None:
                self.ui.sb_tandem_collet_outer_od.setValue(float(tandem_outer))
            if tandem_inner is not None:
                self.ui.sb_tandem_collet_inner_od.setValue(float(tandem_inner))
        finally:
            self.ui.sb_needle_collet_od.blockSignals(False)
            self.ui.sb_tandem_collet_outer_od.blockSignals(False)
            self.ui.sb_tandem_collet_inner_od.blockSignals(False)