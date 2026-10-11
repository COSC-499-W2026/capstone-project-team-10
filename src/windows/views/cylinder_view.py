from PySide6.QtWidgets import QWidget

from classes.app import get_app
from classes.logger import log
from classes.mesh.cylinder import BrachyCylinder

from windows.models.shape_model import ShapeTypes
from windows.ui.cylinder_view_ui import Ui_Cylinder_View
from windows.views.custom_view import display_action, CustomView
from windows.length_field import LengthField, LengthUnit

from settings.reset import getCurrentValues
from OCC.Core.gp import gp_Dir, gp_Ax2, gp_Pnt

materials = {
    ShapeTypes.CYLINDER: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.CHANNEL: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.TANDEM: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.SELECTED: {"rgb": [0.2, 0.55, 0.55], "transparent": True}
}


class CylinderView(CustomView):

    @display_action
    def action_apply_settings(self):
        app = get_app()
        log.debug(f"applying cylinder settings")

        model = app.window.cylindermodel
        cylinder = model.cylinder

        diameter = self.diameter_field.millimetres
        length = self.length_field.millimetres
        add_base = self.ui.cb_add_base.isChecked()

        base_thickness = self.base_thickness_field.millimetres
        base_height = self.base_height_field.millimetres
        
        # update the config_values dict
        app.values.config_values["CONFIG_CYLINDER_DIAMETER"] = diameter
        app.values.config_values["CONFIG_CYLINDER_LENGTH"] = length
        app.values.config_values["CONFIG_BASE_THICKNESS"] = base_thickness
        app.values.config_values["CONFIG_BASE_HEIGHT"] = base_height

        self.diameter = diameter
        self.length = length 
        cylinder = BrachyCylinder(diameter=diameter)
       
        # send the new offset signal
        # The offset is the amount the cylinder has changed compared to the starting_length.
        # The needle points and tandem are adjusted from their original location 
        # (which is determined when they are originally loaded) and the needle points are never modified.
        offset = length - model.starting_length 
        app.signals.height_changed.emit(offset)

        cylinder.enableBase(add_base)  # this will force the cylinder's shape to be recalculated

        model.update_cylinder(cylinder)

        #update the maximium tandem height value allowed to reduce user errors
        get_app().window.navigationmodel.views[3].ui.sb_tandem_height.setMaximum(length)

    def action_update_settings(self, cylinder: BrachyCylinder):    
        log.debug(f"updating cylinder view's settings")
        model = get_app().window.cylindermodel
        
        if model.cylinder is None: return

        diameter = model.cylinder.diameter
        length = model.cylinder.length
        add_base = model.cylinder.expand_base
        
        self.set_dimensions_mm(diameter, length)
        self.ui.cb_add_base.setChecked(add_base)

        self.base_thickness_field.set_millimetres(get_app().values.config_values.get("CONFIG_BASE_THICKNESS", 0.0))
        self.base_height_field.set_millimetres(get_app().values.config_values.get("CONFIG_BASE_HEIGHT", 0.0))

    def set_dimensions_mm(self, diameter: float, length: float) -> None:
        """Load model or config dimensions without interpreting them as display units."""
        self.diameter_field.set_millimetres(diameter)
        self.length_field.set_millimetres(length)

    def action_change_units(self, unit_name: str) -> None:
        """Render pending dimensions in the selected unit without applying the design."""
        unit = LengthUnit(unit_name)
        for field in self.length_fields:
            field.set_unit(unit)

    @display_action
    def on_open(self):
        log.debug(f"view open")
        displaymodel = get_app().window.displaymodel
        displaymodel.set_materials(materials)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Cylinder_View()  # the converted python file from the ui file
        self.ui.setupUi(self)

        self.diameter_field = LengthField(self.ui.spinbox_diameter)
        self.length_field = LengthField(self.ui.spinbox_length)
        self.base_thickness_field = LengthField(self.ui.spinbox_base_thickness)
        self.base_height_field = LengthField(self.ui.spinbox_base_height)
        self.length_fields = (self.diameter_field, self.length_field,
                              self.base_thickness_field, self.base_height_field)

        # Set the spin box values
        config = get_app().values.config_values
        self.set_dimensions_mm(config["CONFIG_CYLINDER_DIAMETER"], config["CONFIG_CYLINDER_LENGTH"])
        self.base_thickness_field.set_millimetres(config.get("CONFIG_BASE_THICKNESS", 0.0))
        self.base_height_field.set_millimetres(config.get("CONFIG_BASE_HEIGHT", 0.0))

        # signals and slots
        self.ui.btn_apply_settings.pressed.connect(self.action_apply_settings)
        self.ui.combobox_units.currentTextChanged.connect(self.action_change_units)

        window = get_app().window
        window.cylindermodel.values_changed.connect(self.action_update_settings)

        self.action_update_settings(window.cylindermodel.cylinder)
