from PySide6.QtWidgets import QWidget, QFileDialog

from classes.app import get_app
from classes.logger import log
from windows.models.shape_model import ShapeTypes
from windows.ui.tandem_view_ui import Ui_Tandem_View
from windows.views.custom_view import display_action, CustomView

from settings.reset import getCurrentValues

materials = {
    ShapeTypes.CYLINDER: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.CHANNEL: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.TANDEM: {"rgb": [0.2, 0.55, 0.55], "transparent": False},
    ShapeTypes.SELECTED: {"rgb": [0.2, 0.8, 0.55], "transparent": True}
}


class TandemView(CustomView):

    @display_action
    def action_clear_tandem(self):
        log.debug(f"action: clearing tandem")
        self.tandemmodel.clear_tandem()

    @display_action
    def action_set_tandem(self):
        log.debug(f"action: generate a tandem")

        # assign the tandemmodel attributes with the new values
        tan = self.tandemmodel
        tan.threading_diameter = self.ui.sb_threading_diameter.value()
        tan.threading_depth = self.ui.sb_threading_depth.value()
        tan.tandem_diameter = self.ui.sp_channel_diameter.value()
        tan.stopper_diameter = self.ui.sp_stopper_diameter.value()
        tan.tip_angle = self.ui.sp_bend_angle.value()
        tan.bend_radius = self.ui.sb_bend_radius.value()
        tan.tandem_length =  self.ui.sb_tandem_height.value()
        # set the tandem with the new values
        tan.set_tandem()

        #sets tandem rotation to the value in the box and then updates the spin box
        window = get_app().window
        if(tan.hasTandemInDICOM):
            if(not self.hasShownRotationWarning):
                if(round(tan.protation,2) != round(window.navigationmodel.views[3].ui.tandem_rotation_2.value(),2)):
                    #will reset rotation value to rotation value in the plan
                    self.hasShownRotationWarning=True
                    window.tandem_rotation_warning()
        
        tan = get_app().window.tandemmodel
        tan.change_tandem_rotation(self.ui.tandem_rotation_2.value())

        #updates the spin box value of rotation
        rotation = window.tandemmodel.rotation
        self.ui.tandem_rotation.setValue(rotation)
        self.ui.tandem_rotation_2.setValue(rotation)
        # update the config_values dict
        # merge, so a setting the snapshot does not list keeps its value
        get_app().values.config_values.update(getCurrentValues())


    @display_action
    def action_import_tandem(self):
        log.debug(f"action: import a tandem")
        # file dialog to choose file
        filename = QFileDialog.getOpenFileName(
            self, 'Select Tandem Tool Model', "", "Supported files (*.stp *.step)")[0]

        if not filename:  # no folder selected?
            log.info("no valid filename selected for importing")
            return

        log.info(f"file {filename} has been selected")

        self.tandemmodel.import_tandem(filename)
        
        #sets tandem rotation to the value in the box
        window = get_app().window
        tan = window.tandemmodel
        if(tan.hasTandemInDICOM):
            if(not self.hasShownRotationWarning):
                if(round(tan.protation,2) != round(window.navigationmodel.views[3].ui.tandem_rotation.value(),2)):
                    self.hasShownRotationWarning=True
                    window.tandem_rotation_warning()
        
        tan.change_tandem_rotation(self.ui.tandem_rotation.value())
        
        self.update_settings()

    @display_action
    def action_set_import(self):
        # get the current value in the spin box
        offset = self.ui.sb_height_offset.value()
        # use the spin box value as the new height offset value
        self.tandemmodel.set_import_height_offset(offset)

        #sets tandem rotation to the value in the box and then updates the spin box
        window = get_app().window
        tan = window.tandemmodel
        if(tan.hasTandemInDICOM):
            if(not self.hasShownRotationWarning):
                if(round(tan.protation,2) != round(window.navigationmodel.views[3].ui.tandem_rotation.value(),2)):
                    self.hasShownRotationWarning=True
                    window.tandem_rotation_warning()
        tan.change_tandem_rotation(self.ui.tandem_rotation.value())
        self.ui.tandem_rotation_2.setValue(self.ui.tandem_rotation.value())


    def on_close(self):
        log.debug(f"on view close")

    @display_action
    def on_open(self):
        log.debug(f"on view open")

        displaymodel = get_app().window.displaymodel
        displaymodel.set_materials(materials)
        self.tandemmodel.update_display()

        self.update_settings()

    def update_settings(self):
        log.debug(f"updating settings")
        tandem_diameter = self.tandemmodel.tandem_diameter
        self.ui.sp_channel_diameter.setValue(tandem_diameter)

        stopper_diameter = self.tandemmodel.stopper_diameter
        self.ui.sp_stopper_diameter.setValue(stopper_diameter)

        tip_angle = self.tandemmodel.tip_angle
        self.ui.sp_bend_angle.setValue(tip_angle)

        bend_radius = self.tandemmodel.bend_radius
        self.ui.sb_bend_radius.setValue(bend_radius)

        tandem_length = self.tandemmodel.tandem_length
        self.ui.sb_tandem_height.setValue(tandem_length)
        #self.ui.sb_height_offset.setValue(tandem_length)

        # set the spin box value of height offset to the value currently in use
        height_offset = self.tandemmodel.mesh_offset
        self.ui.sb_height_offset.setValue(height_offset)

        tandem_rotation = self.tandemmodel.rotation
        self.ui.tandem_rotation.setValue(tandem_rotation)
        self.ui.tandem_rotation_2.setValue(tandem_rotation)

        tandem_threading_diameter = self.tandemmodel.threading_diameter
        tandem_threading_depth = self.tandemmodel.threading_depth
        self.ui.sb_threading_depth.setValue(tandem_threading_depth)
        self.ui.sb_threading_diameter.setValue(tandem_threading_diameter)

        filepath = self.tandemmodel.filepath
        self.ui.label_5.setText(f"Model filepath:\n{filepath}")

    def __init__(self):
        super().__init__()
        self.ui = Ui_Tandem_View()  # the converted python file from the ui file
        self.ui.setupUi(self)
        self.tandemmodel = get_app().window.tandemmodel
        self.hasShownRotationWarning = False

        # signals and slots
        self.ui.btn_apply.pressed.connect(self.action_set_tandem)
        self.ui.btn_clear_generate.pressed.connect(self.action_clear_tandem)
        self.ui.btn_import.pressed.connect(self.action_import_tandem)
        self.ui.btn_clear_import.pressed.connect(self.action_clear_tandem)     
        self.ui.btn_apply_import.pressed.connect(self.action_set_import)

        self.update_settings()
