from PySide6.QtWidgets import QWidget, QListWidgetItem, QMessageBox

from classes.app import get_app
from classes.logger import log
from windows.models.shape_model import ShapeTypes
from windows.ui import arrows_rc  # registers the :/arrows/ images used below
from windows.ui.channels_view_ui import Ui_Channels_View
from windows.views.custom_view import display_action, CustomView

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


class ChannelsView(CustomView):

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
        
        label = self.channelsmodel.get_selected_channel()
        is_disabled = self.channelsmodel.is_channel_disabled(label)
        is_tandem = self.channelsmodel.is_channel_tandem(label)
        lister = self.ui.listwidget_channels
        if selected_channel is None:
            # clear the list's highlight and current item so it matches the model,
            # and so clicking the same channel again emits currentItemChanged
            lister.blockSignals(True)
            lister.setCurrentRow(-1)
            lister.blockSignals(False)
        for i in range(lister.count()):
            text = lister.item(i).text()
            row = i
            if(text==label):
                lister.scrollToItem(lister.item(row))
                lister.item(row).setSelected(True)
        if is_disabled: self.ui.btn_enable.setText("Enable")
        else: self.ui.btn_enable.setText("Disable")

        if is_tandem: self.ui.btn_set_tandem.setText("Clear Tandem")
        else: self.ui.btn_set_tandem.setText("Set as Tandem")

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

        #sets default needle length
        config_values = get_app().values.config_values
        self.ui.sb_needle_length.setValue(config_values.get("CONFIG_DEADSPACE"))
        self.ui.sb_threading_dept.setValue(config_values.get("CONFIG_CHANNELS_THREADING_DEPTH"))
        self.ui.sb_threading_diameter.setValue(config_values.get("CONFIG_CHANNELS_THREADING_DIAMETER"))

        # signals and slots
        self.ui.btn_apply_settings.pressed.connect(self.action_apply_settings)
        self.ui.listwidget_channels.currentItemChanged.connect(self.action_select_channel)
        self.ui.btn_enable.pressed.connect(self.action_toggle_channel_disable)
        self.ui.btn_set_tandem.pressed.connect(self.action_set_tandem)

        self.channelsmodel = get_app().window.channelsmodel
        self.channelsmodel.values_changed.connect(self.action_update_settings)

        self.action_update_settings()
