from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QListWidgetItem, QMessageBox, QPushButton, QWidget,
)

from classes.app import get_app
from classes.info import USER_PATH
from classes.logger import log
from classes.mesh.channel import Translation
from windows.models.channels_model import ChannelStatus
from windows.models.shape_model import ShapeTypes
from windows.ui import arrows_rc  # registers the :/arrows/ images used below
from windows.ui.channels_view_ui import Ui_Channels_View
from windows.views.custom_view import display_action, CustomView

from settings.defaults import MINIMUM_CHANNEL_DIAMETER_MM
from settings.needle_templates import (
    LIBRARY_FILE_NAME, NeedleTemplate, NeedleTemplateError, load_templates, make_template, save_template,
)
from settings.reset import getCurrentValues


materials = {
    ShapeTypes.CYLINDER: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.CHANNEL: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.TANDEM: {"rgb": [0.8, 0.8, 0.8], "transparent": True},
    ShapeTypes.SELECTED: {"rgb": [0.2, 0.2, 0.7], "transparent": True}
}

# black arrows for the spin boxes. without them, macOS in dark mode draws the native arrows
# white on the white field the .ui stylesheets paint, and they vanish
spin_box_arrows = """
QDoubleSpinBox::up-arrow { image: url(:/arrows/spin_up.png); width: 7px; height: 7px; }
QDoubleSpinBox::down-arrow { image: url(:/arrows/spin_down.png); width: 7px; height: 7px; }
"""


@dataclass(frozen=True)
class ChannelRowStyle:
    """How a channel's list row shows its status. Each colour has its own bold and italic
    pair, so colour is never the only cue."""
    background: QBrush
    bold: bool
    italic: bool


STATUS_ROW_STYLES = {
    ChannelStatus.STANDARD: ChannelRowStyle(QBrush(), bold=False, italic=False),
    ChannelStatus.OWN_DIAMETER: ChannelRowStyle(QBrush(QColor(255, 214, 153)), bold=True, italic=False),
    ChannelStatus.DISABLED: ChannelRowStyle(QBrush(QColor(220, 220, 220)), bold=False, italic=True),
    ChannelStatus.TANDEM: ChannelRowStyle(QBrush(QColor(204, 224, 255)), bold=True, italic=True),
}


def channel_status_text(status: ChannelStatus, diameter: float) -> str:
    if status is ChannelStatus.TANDEM: return "Tandem channel, not cut as a needle"
    if status is ChannelStatus.DISABLED: return "Disabled, not cut into the cylinder"
    if status is ChannelStatus.OWN_DIAMETER: return f"Own diameter {diameter:.3f} mm"
    return f"Channels diameter {diameter:.3f} mm"


def moved_text(translation: Translation) -> str:
    dx, dy, dz = translation
    return f"Moved by X {dx:g}, Y {dy:g}, Z {dz:g} mm from the plan"


class MoveChannelDialog(QDialog):
    """Asks how far to move one channel from its plan position, with X, Y and Z in mm.

    It has no parent, like the app's other dialogs: parented to the tab it would inherit the
    tab's spin box stylesheet. The fields start at the channel's current move, so OK with
    nothing edited changes nothing, and Reset to plan position zeroes all three.
    """
    RANGE_MM = 300.0  # the longest cylinder the Cylinder tab allows

    def __init__(self, label: str, translation: Translation):
        super().__init__()
        self.setWindowTitle(f"Move {label}")
        form = QFormLayout(self)
        self.spin_x, self.spin_y, self.spin_z = (self.make_spin_box(value) for value in translation)
        for axis, spin_box in (("X", self.spin_x), ("Y", self.spin_y), ("Z", self.spin_z)):
            form.addRow(axis, spin_box)
        self.btn_reset = QPushButton("Reset to plan position")
        self.btn_reset.setAutoDefault(False)  # Return must press OK, never Reset
        self.btn_reset.clicked.connect(self.reset)
        form.addRow(self.btn_reset)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def make_spin_box(self, value: float) -> QDoubleSpinBox:
        spin_box = QDoubleSpinBox()
        spin_box.setRange(-self.RANGE_MM, self.RANGE_MM)
        spin_box.setDecimals(3)
        spin_box.setSuffix(" mm")
        spin_box.setValue(value)
        return spin_box

    def reset(self) -> None:
        for spin_box in (self.spin_x, self.spin_y, self.spin_z):
            spin_box.setValue(0.0)

    def translation(self) -> Translation:
        return (self.spin_x.value(), self.spin_y.value(), self.spin_z.value())


class ChannelsView(CustomView):

    @display_action
    def action_move_channel(self, item: QListWidgetItem) -> None:
        label = item.text()
        if self.channelsmodel.is_channel_tandem(label): return
        current = self.channelsmodel.channels[label].translation
        translation = self.ask_translation(label, current)
        if translation is None or translation == current: return
        log.info(f"moving {label} by {translation} mm from the plan")
        self.channelsmodel.move_channel(label, *translation)

    def ask_move(self, label: str, translation: Translation) -> Translation | None:
        dialog = MoveChannelDialog(label, translation)
        if dialog.exec() != QDialog.DialogCode.Accepted: return None
        return dialog.translation()

    @display_action
    def action_select_channel(self, item: QListWidgetItem, *args):
        log.debug(f"action: select channel")
        log.debug(f"{args}")
        if type(item) is type(None): return None
        else: label = item.text()

        log.debug(f"selecting {label} channel")    
        try:
            self.channelsmodel.set_selected_channels(label)
        except Exception as error_message:
            log.critical(f"failed selecting channel from list view: \n{error_message}")

    @display_action
    def action_apply_settings(self):
        log.debug(f"action: apply settings")
        app = get_app()
        # update config_values dict for needles
        needles_length = self.ui.sb_needle_length.value()
        diameter = self.ui.spinbox_diameter.value()
        threading_depth = self.ui.sb_threading_dept.value()
        threading_diameter= self.ui.sb_threading_diameter.value()
        if(diameter != app.values.config_values["CONFIG_CHANNELS_DIAMETER"] or \
           needles_length != app.values.config_values["CONFIG_DEADSPACE"] or \
           app.window.channelsmodel.threading_depth != threading_depth or \
            app.window.channelsmodel.threading_diamenter != threading_diameter):
            log.debug(f"setting channel diameters to: {diameter}")
            app.window.channelsmodel.threading_depth =  threading_depth
            app.window.channelsmodel.threading_diamenter = threading_diameter
            app.values.config_values["CONFIG_CHANNELS_THREADING_DEPTH"] = app.window.channelsmodel.threading_depth
            app.values.config_values["CONFIG_CHANNELS_THREADING_DIAMETER"] = app.window.channelsmodel.threading_diamenter
            app.values.config_values["CONFIG_CHANNELS_DIAMETER"] = diameter
            app.values.config_values["CONFIG_DEADSPACE"] = needles_length
            self.channelsmodel.set_diameter(diameter)
        
    @display_action
    def action_set_selected_shapes(self, *args, **kwargs):
        self.channelsmodel.set_selected_shapes(*args)

    @display_action
    def action_set_tandem(self):
        data = get_app().window.dicommodel.data
        window = get_app().window
        tan = window.tandemmodel
        log.debug(f"setting channel's tandem status")

        model = get_app().window.channelsmodel
        channel_label = model.get_selected_channel()

        # set or clear the tandem channel
        
        #stores old tandem label in canse user desides they want to 
        #revert to plan value when prompted
        temp_label=data.tandem_channel

        label = None
        if channel_label != data.tandem_channel: 
            label = channel_label
            model.set_tandem(label)
        
        answer = QMessageBox.Yes
        if(tan.hasTandemInDICOM):
            if(not window.navigationmodel.views[3].hasShownRotationWarning):
                if(round(tan.protation,2) != round(window.tandemmodel.rotation,2)):
                    window.navigationmodel.views[3].hasShownRotationWarning=True
                    answer = window.tandem_rotation_warning()
        #If the user wishes to proceed then do this, if not then do not
        if(answer == QMessageBox.No):
            label = None
            model.set_tandem(temp_label)


        #updates the spin box value of rotation
        rotation = window.tandemmodel.rotation
        window.navigationmodel.views[3].ui.tandem_rotation.setValue(rotation)
        window.navigationmodel.views[3].ui.tandem_rotation_2.setValue(rotation)

    @display_action
    def action_toggle_channel_disable(self):
        log.debug(f"toggling channel's disabled status")
        model = get_app().window.channelsmodel
        channel_label = model.get_selected_channel()   
        model.toggle_channel_enabled(channel_label)

    @display_action
    def action_apply_channel_diameter(self):
        log.debug(f"action: give the selected channel its own diameter")
        label = self.channelsmodel.get_selected_channel()
        self.channelsmodel.set_channel_diameter(label, self.ui.sb_channel_diameter.value())

    @display_action
    def action_clear_channel_diameter(self):
        log.debug(f"action: return the selected channel to the channels diameter")
        self.channelsmodel.clear_channel_diameter(self.channelsmodel.get_selected_channel())

    def action_load_templates(self) -> None:
        try:
            self.show_templates(load_templates(self.templates_path))
        except NeedleTemplateError as error:
            self.show_templates(())
            self.ui.label_template_status.setText(str(error))

    def show_templates(self, templates: tuple[NeedleTemplate, ...]) -> None:
        self.templates = templates
        self.ui.cb_needle_templates.clear()
        self.ui.cb_needle_templates.addItems([f"{template.name}  {template.diameter_mm:.3f} mm" for template in templates])
        self.ui.btn_apply_template.setEnabled(len(templates) > 0)

    def action_save_template(self) -> None:
        try:
            template = make_template(self.ui.le_template_name.text(), self.ui.sb_channel_diameter.value())
            self.show_templates(save_template(self.templates_path, template))
            self.ui.label_template_status.setText(f"Saved {template.name}")
        except NeedleTemplateError as error:
            self.ui.label_template_status.setText(str(error))

    @display_action
    def action_apply_template(self) -> None:
        template = self.templates[self.ui.cb_needle_templates.currentIndex()]
        self.channelsmodel.set_channel_diameter(self.channelsmodel.get_selected_channel(), template.diameter_mm)

    def create_channels_list(self):
        # channels list
        selected_channel = self.channelsmodel.get_selected_channel()
        self.ui.listwidget_channels.blockSignals(True)  # prevents accidently emitting signals
        self.ui.listwidget_channels.clear()
        for row, channel in enumerate(self.channelsmodel.channels.values()):
            new_item = QListWidgetItem()
            new_item.setText(channel.label)
            self.ui.listwidget_channels.addItem(new_item)
            if selected_channel is not None and \
               selected_channel == channel.label:
                self.ui.listwidget_channels.setCurrentRow(row)
        self.ui.listwidget_channels.blockSignals(False)
        self.mark_channel_statuses()

    def mark_channel_statuses(self) -> None:
        lister = self.ui.listwidget_channels
        for label, channel in self.channelsmodel.channels.items():
            status = self.channelsmodel.channel_status(label)
            style = STATUS_ROW_STYLES[status]
            for item in lister.findItems(label, Qt.MatchFlag.MatchExactly):
                font = item.font()
                font.setBold(style.bold)
                font.setItalic(style.italic)
                font.setUnderline(self.channelsmodel.is_channel_moved(label))
                item.setFont(font)
                item.setBackground(style.background)
                tooltip = channel_status_text(status, channel.get_diameter())
                if self.channelsmodel.is_channel_moved(label): tooltip += "\n" + moved_text(channel.translation)
                item.setToolTip(tooltip)
    
    def action_update_settings(self):
        log.debug(f"updating channels view")
        
        # diameter spin box
        self.ui.spinbox_diameter.setValue(self.channelsmodel.diameter)
        # needle channels spin box
        self.ui.sb_needle_length.setValue(get_app().values.config_values.get("CONFIG_DEADSPACE"))

        selected_channel = self.channelsmodel.get_selected_channel()
        # selected channel
        # enable/disable buttons if any channel is selected
        any_selected = selected_channel != None
        self.ui.btn_enable.setEnabled(any_selected)
        self.ui.btn_set_tandem.setEnabled(any_selected)
        self.ui.group_selected_channel.setEnabled(any_selected)
        if any_selected:
            self.ui.sb_channel_diameter.setValue(self.channelsmodel.channels[selected_channel].get_diameter())
        self.ui.btn_clear_channel_diameter.setEnabled(any_selected and self.channelsmodel.has_own_diameter(selected_channel))
        
        label = self.channelsmodel.get_selected_channel()
        is_disabled = self.channelsmodel.is_channel_disabled(label)
        is_tandem = self.channelsmodel.is_channel_tandem(label)
        lister = self.ui.listwidget_channels
        selected_row = -1
        for row in range(lister.count()):
            if lister.item(row).text() == label:
                selected_row = row
        # make the model's channel the list's current item, or none, however it was
        # selected, so clicking any other channel in the list emits currentItemChanged
        with QSignalBlocker(lister):
            lister.setCurrentRow(selected_row)
        if selected_row != -1:
            lister.scrollToItem(lister.item(selected_row))
        if is_disabled: self.ui.btn_enable.setText("Enable")
        else: self.ui.btn_enable.setText("Disable")

        if is_tandem: self.ui.btn_set_tandem.setText("Clear Tandem")
        else: self.ui.btn_set_tandem.setText("Set as Tandem")
        self.mark_channel_statuses()

    def on_close(self):
        log.debug(f"on close")

        channelsmodel = get_app().window.channelsmodel
        channelsmodel.clear_selected_channels()

        try:         
            canvas = get_app().window.canvas
            canvas.sig_topods_selected.disconnect(self.action_set_selected_shapes)
        except RuntimeError as error_message:  # incase the signal isn't connected
            log.warning(f"{error_message}")

    @display_action
    def on_open(self):
        log.debug(f"on open")

        canvas = get_app().window.canvas
        canvas.sig_topods_selected.connect(self.action_set_selected_shapes)

        displaymodel = get_app().window.displaymodel
        displaymodel.set_materials(materials)
        self.channelsmodel.update()

        self.action_update_settings()

    def __init__(self):
        super().__init__()
        self.ui = Ui_Channels_View()  # the converted python file from the ui file
        self.ui.setupUi(self)
        self.setStyleSheet(spin_box_arrows)
        self.is_active = False
        self.ask_translation: Callable[[str, Translation], Translation | None] = self.ask_move

        #sets default needle length
        config_values = get_app().values.config_values
        self.ui.sb_needle_length.setValue(config_values.get("CONFIG_DEADSPACE"))
        self.ui.sb_threading_dept.setValue(config_values.get("CONFIG_CHANNELS_THREADING_DEPTH"))
        self.ui.sb_threading_diameter.setValue(config_values.get("CONFIG_CHANNELS_THREADING_DIAMETER"))

        self.ui.sb_channel_diameter.setMinimum(MINIMUM_CHANNEL_DIAMETER_MM)
        self.templates_path = USER_PATH.joinpath(LIBRARY_FILE_NAME)
        self.action_load_templates()

        # signals and slots
        self.ui.btn_apply_settings.pressed.connect(self.action_apply_settings)
        self.ui.btn_apply_channel_diameter.pressed.connect(self.action_apply_channel_diameter)
        self.ui.btn_clear_channel_diameter.pressed.connect(self.action_clear_channel_diameter)
        self.ui.btn_save_template.pressed.connect(self.action_save_template)
        self.ui.btn_apply_template.pressed.connect(self.action_apply_template)
        self.ui.listwidget_channels.currentItemChanged.connect(self.action_select_channel)
        self.ui.listwidget_channels.itemDoubleClicked.connect(self.action_move_channel)
        self.ui.btn_enable.pressed.connect(self.action_toggle_channel_disable)
        self.ui.btn_set_tandem.pressed.connect(self.action_set_tandem)

        self.channelsmodel = get_app().window.channelsmodel
        self.channelsmodel.values_changed.connect(self.action_update_settings)

        self.action_update_settings()
