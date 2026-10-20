from datetime import datetime, timezone
from uuid import uuid4

from PySide6.QtWidgets import QFrame, QLayout, QListWidgetItem, QScrollArea, QVBoxLayout, QWidget

from classes.app import get_app
from classes.info import USER_PATH
from classes.logger import log
from classes.mesh.cylinder import BrachyCylinder, TipShape, tip_shape_from_config
from classes.mesh.notch import NotchSettings, notch_settings_from_config

from windows.models.shape_model import ShapeTypes
from windows.ui.cylinder_view_ui import Ui_Cylinder_View
from windows.views.custom_view import display_action, CustomView
from windows.length_field import LengthField, LengthUnit

from settings.cylinder_templates import (
    LIBRARY_FILE_NAME, CylinderDesign, CylinderTemplate, CylinderTemplateError, add_template, load_templates,
    make_template,
)
from settings.reset import getCurrentValues
from OCC.Core.gp import gp_Dir, gp_Ax2, gp_Pnt

materials = {
    ShapeTypes.CYLINDER: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.CHANNEL: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.TANDEM: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.SELECTED: {"rgb": [0.2, 0.55, 0.55], "transparent": True}
}


def template_summary(template: CylinderTemplate) -> str:
    """A saved template's tooltip: its note, its dates and its cylinder in one line, with no colons."""
    design = template.design
    tip = TipShape.FLAT if design.flat_tip else TipShape.DOME
    lines = [template.note] if template.note else []
    lines += [f"Created {template.created.astimezone():%d %b %Y}",
              f"Modified {template.modified.astimezone():%d %b %Y}",
              f"{design.diameter_mm:.2f} mm by {design.length_mm:g} mm, {tip.value}"]
    return "\n".join(lines)


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
        app.values.config_values["CONFIG_CYLINDER_FLAT_TIP"] = int(self.selected_tip() is TipShape.FLAT)
        notch = self.notch_settings()
        app.values.config_values["CONFIG_NOTCH_ENABLED"] = int(notch.enabled)
        app.values.config_values["CONFIG_NOTCH_ANGLE"] = notch.angle
        app.values.config_values["CONFIG_NOTCH_WIDTH"] = notch.width
        app.values.config_values["CONFIG_NOTCH_DEPTH"] = notch.depth
        app.values.config_values["CONFIG_NOTCH_HEIGHT"] = notch.height

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
        self.set_notch_settings(model.cylinder.notch_settings)
        self.set_tip(model.cylinder.tip)

    def set_dimensions_mm(self, diameter: float, length: float) -> None:
        """Load model or config dimensions without interpreting them as display units."""
        self.diameter_field.set_millimetres(diameter)
        self.length_field.set_millimetres(length)

    def selected_tip(self) -> TipShape:
        """Read the Tip Shape choice. Its items are the TipShape values."""
        return TipShape(self.ui.combobox_tip.currentText())

    def set_tip(self, tip: TipShape) -> None:
        """Show the given tip without applying it."""
        self.ui.combobox_tip.setCurrentText(tip.value)

    def notch_settings(self) -> NotchSettings:
        """Read the notch controls, lengths in mm."""
        return NotchSettings(
            enabled=self.ui.cb_add_notch.isChecked(),
            angle=self.ui.spinbox_notch_angle.value(),
            width=self.notch_width_field.millimetres,
            depth=self.notch_depth_field.millimetres,
            height=self.notch_height_field.millimetres)

    def set_notch_settings(self, notch: NotchSettings) -> None:
        """Show the given notch in the controls without applying it."""
        self.ui.cb_add_notch.setChecked(notch.enabled)
        self.ui.spinbox_notch_angle.setValue(notch.angle)
        self.notch_width_field.set_millimetres(notch.width)
        self.notch_depth_field.set_millimetres(notch.depth)
        self.notch_height_field.set_millimetres(notch.height)
        self.action_enable_notch_fields(notch.enabled)

    def action_enable_notch_fields(self, enabled: bool) -> None:
        """Grey out the notch controls while the notch is off."""
        for spinbox in (self.ui.spinbox_notch_angle, self.ui.spinbox_notch_width,
                        self.ui.spinbox_notch_depth, self.ui.spinbox_notch_height):
            spinbox.setEnabled(enabled)

    def cylinder_design(self) -> CylinderDesign:
        """Read the tab's 11 settings, lengths in mm whatever Units shows."""
        notch = self.notch_settings()
        return CylinderDesign(
            diameter_mm=self.diameter_field.millimetres,
            length_mm=self.length_field.millimetres,
            collar_enabled=self.ui.cb_add_base.isChecked(),
            collar_thickness_mm=self.base_thickness_field.millimetres,
            collar_height_mm=self.base_height_field.millimetres,
            notch_enabled=notch.enabled,
            notch_angle_deg=notch.angle,
            notch_width_mm=notch.width,
            notch_depth_mm=notch.depth,
            notch_height_mm=notch.height,
            flat_tip=self.selected_tip() is TipShape.FLAT)

    def action_load_templates(self) -> None:
        """Show every saved template, or none, with the reason, if the library cannot be read."""
        try:
            self.show_templates(load_templates(self.templates_path))
        except CylinderTemplateError as error:
            self.show_templates(())
            self.ui.label_template_status.setText(str(error))

    def show_templates(self, templates: tuple[CylinderTemplate, ...]) -> None:
        self.templates = templates
        self.ui.list_templates.clear()
        for template in templates:
            row = QListWidgetItem(template.name)
            row.setToolTip(template_summary(template))
            self.ui.list_templates.addItem(row)

    def action_save_template(self) -> None:
        """Save the tab's settings under the typed name and note, or say in the status line why not."""
        now = datetime.now(timezone.utc)
        try:
            template = make_template(uuid4().hex, self.ui.le_template_name.text(), self.ui.le_template_note.text(),
                                     self.cylinder_design(), now, now)
            self.show_templates(add_template(self.templates_path, template))
            self.ui.label_template_status.setText(f"Saved {template.name}")
        except CylinderTemplateError as error:
            self.ui.label_template_status.setText(str(error))

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
        # the tab's rows do not fit brachify's default window, so they scroll rather than squeeze
        content = QWidget()
        self.ui.setupUi(content)
        # the .ui's 290 px minimum would let the scroll area squeeze the rows, so the layout sets it
        self.ui.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        scroll = QScrollArea(self)
        scroll.setObjectName("scroll_cylinder")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        self.diameter_field = LengthField(self.ui.spinbox_diameter)
        self.length_field = LengthField(self.ui.spinbox_length)
        self.base_thickness_field = LengthField(self.ui.spinbox_base_thickness)
        self.base_height_field = LengthField(self.ui.spinbox_base_height)
        self.notch_width_field = LengthField(self.ui.spinbox_notch_width)
        self.notch_depth_field = LengthField(self.ui.spinbox_notch_depth)
        self.notch_height_field = LengthField(self.ui.spinbox_notch_height)
        self.length_fields = (self.diameter_field, self.length_field,
                              self.base_thickness_field, self.base_height_field,
                              self.notch_width_field, self.notch_depth_field,
                              self.notch_height_field)

        # Set the spin box values
        config = get_app().values.config_values
        self.set_dimensions_mm(config["CONFIG_CYLINDER_DIAMETER"], config["CONFIG_CYLINDER_LENGTH"])
        self.base_thickness_field.set_millimetres(config.get("CONFIG_BASE_THICKNESS", 0.0))
        self.base_height_field.set_millimetres(config.get("CONFIG_BASE_HEIGHT", 0.0))
        self.set_notch_settings(notch_settings_from_config(config))
        self.set_tip(tip_shape_from_config(config))
        self.templates_path = USER_PATH.joinpath(LIBRARY_FILE_NAME)
        self.action_load_templates()

        # signals and slots
        self.ui.btn_save_template.pressed.connect(self.action_save_template)
        self.ui.cb_add_notch.toggled.connect(self.action_enable_notch_fields)
        self.ui.btn_apply_settings.pressed.connect(self.action_apply_settings)
        self.ui.combobox_units.currentTextChanged.connect(self.action_change_units)

        window = get_app().window
        window.cylindermodel.values_changed.connect(self.action_update_settings)

        self.action_update_settings(window.cylindermodel.cylinder)
