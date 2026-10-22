from enum import Enum, auto
from math import isfinite

from PySide6.QtCore import QObject, Signal

from classes.app import get_app
from classes.dicom.data import DicomData
from classes.logger import log
from classes.mesh.channel import NeedleChannel
from settings.defaults import MINIMUM_CHANNEL_DIAMETER_MM
from windows.models.shape_model import ShapeModel, ShapeTypes

CHANNELS_LABEL = "applicator_"


class ChannelStatus(Enum):
    """How a channel differs from the Channels settings, the first that applies in this order."""
    TANDEM = auto()  # the tandem's path, so it is not cut as a needle
    DISABLED = auto()  # left out of the cut and the PDF
    OWN_DIAMETER = auto()  # cut at its own diameter, not the Channels Diameter
    STANDARD = auto()


class ChannelsModel(QObject):

    values_changed = Signal()
    tandem_changed = Signal(NeedleChannel)

    def clear_selected_channels(self):
        self.selected_channels = []
        self.update()

    def get_selected_channel(self) -> str:
        if not self.selected_channels: return None
        return self.selected_channels[0]
    
    def get_tandem_channel(self) -> NeedleChannel:
        data = get_app().window.dicommodel.data
        if not data.tandem_channel: return None
        return self.channels[data.tandem_channel]

    def get_visible_channels(self) -> list[NeedleChannel]:
        """Returns a list of NeedleChannel where the objects are not disabled"""
        return [channel 
                for channel in self.channels.values() 
                if not self.is_channel_disabled(channel.label)]

    def is_channel_disabled(self, label: str) -> bool:
        return label in self.disabled_channels
    
    def is_channel_tandem(self, label:str) -> bool:
        data = get_app().window.dicommodel.data
        return label == data.tandem_channel

    def channel_status(self, label: str) -> ChannelStatus:
        if self.is_channel_tandem(label): return ChannelStatus.TANDEM
        if self.is_channel_disabled(label): return ChannelStatus.DISABLED
        if self.has_own_diameter(label): return ChannelStatus.OWN_DIAMETER
        return ChannelStatus.STANDARD

    # Slotted to Dicom Model's update
    def load_data(self, data: DicomData):
        self.selected_channels = []
        self.channels = {}
        self.disabled_channels = []
        self.own_diameters = {}
        log.debug("### Importing RP Data ###")

        for i in range(len(data.channels_rois)):
            roi_number = f"{data.channels_rois[i]}"
            channel_id = f"{data.channels_labels[i]}"
            channel_number = f"{data.channel_numbers[i]}"
            points = data.channel_paths[i]

            # to print the list of points without quotes
            points_list = f"Raw points: {points}"
            log.debug(points_list.replace("'", ""))

            needle = NeedleChannel(
                roi_number=roi_number,
                channel_number=channel_number,
                label=channel_id,
                points=points)
            self.channels[needle.label]= needle

            #set tandem channel
            if "tandem" in channel_id.lower():
                self.set_tandem(channel_id)

        self.update()

    def set_diameter(self, diameter: float):
        self.diameter = diameter

        # every channel is rebuilt so new threading reaches it, keeping a channel's own diameter
        for label, channel in self.channels.items():
            channel.set_diameter(self.own_diameters.get(label, diameter))
        self.update()

    def set_channel_diameter(self, label: str, diameter: float) -> None:
        if not isfinite(diameter) or diameter < MINIMUM_CHANNEL_DIAMETER_MM:
            raise ValueError(f"{label} needs a diameter of at least {MINIMUM_CHANNEL_DIAMETER_MM} mm, not {diameter}")
        channel = self.channels[label]
        self.own_diameters[label] = diameter
        channel.set_diameter(diameter)
        self.update()

    def clear_channel_diameter(self, label: str) -> None:
        self.own_diameters.pop(label, None)
        self.channels[label].set_diameter(NeedleChannel.default_diameter())
        self.update()

    def has_own_diameter(self, label: str) -> bool:
        return label in self.own_diameters

    def move_channel(self, label: str, dx: float, dy: float, dz: float) -> None:
        channel = self.channels[label]  # a missing label raises KeyError before anything is stored
        if not all(isfinite(value) for value in (dx, dy, dz)):
            raise ValueError(f"{label} cannot move by {dx}, {dy}, {dz}")
        if self.is_channel_tandem(label):
            raise ValueError(f"{label} is the tandem channel and cannot be moved")
        channel.set_translation((dx, dy, dz))
        self.update()

    def is_channel_moved(self, label: str) -> bool:
        return self.channels[label].translation != (0.0, 0.0, 0.0)

    def set_selected_channels(self, *args):
        log.debug(f"setting selected channels")
        self.selected_channels =[]
        if len(args) < 1: raise ValueError("no arguements made!")
        
        # if using indexes to match to the channel's label
        if type(args[0]) is type(int):  # index of the selected channel(s)
            channels = [channel.label for channel in self.channels.values()]
            for index in args:
                self.selected_channels.append(channels[index])
            self.update()
            return None

        elif type(args[0] is type(str)):  # label of selected channel
            self.selected_channels = args
            self.update()
            try:
                log.debug("start selecting row")
                lister = get_app().window.navigationmodel.views[2].ui.listwidget_channels
                lister.blockSignals(True)
                row = lister.row(lister.currentItem())
                lister.scrollToItem(lister.item(row))
                lister.item(row).setSelected(True)
                lister.setFocus()
                #lister.setStyleSheet("QListView::item:selected{background-color: rgb(205,232,255);}")
                log.warning("row selected successfully")
                lister.blockSignals(False)
            except Exception as e:
                log.error(e)
            return None
        
        else:
            raise ValueError(f"wrong value type {type(args[0])}")
    
    def set_selected_shapes(self, *args):
        log.debug(f"setting selected shapes")

        try:
            self.selected_channels =[]
            for compound in args[0]:
                for label, needle in self.channels.items():
                    if compound.IsEqual(needle.shape()):
                        self.selected_channels.append(label)
                        break
            self.update()
        except Exception as error_message:
            log.critical(f"error while setting selected shapes from viewport:\n{error_message}")

    def set_tandem(self, label:str) -> None:
        if label and self.is_channel_moved(label):
            raise ValueError(f"{label} has been moved and cannot be the tandem, reset its move first")
        data = get_app().window.dicommodel.data
        old_label = data.tandem_channel
        if old_label and old_label in self.disabled_channels:
            self.disabled_channels.remove(old_label)

        data.tandem_channel = label
        if not label in self.disabled_channels:
            self.disabled_channels.append(label)

        self.update()
        self.tandem_changed.emit(self.get_tandem_channel())

    def toggle_channel_enabled(self, label: str):
        log.debug(f"Toggling channel enable")
        if label in self.disabled_channels:
            self.disabled_channels.remove(label)
        else:
            self.disabled_channels.append(label)
        log.debug(f"{self.disabled_channels}")
        self.update()

    def update(self):
        self.values_changed.emit()
        self.update_display()

    def update_display(self):
        shapes = [ShapeModel(
            label=channel.label,
            shape=channel.shape(),
            shape_type=ShapeTypes.CHANNEL
        ) for channel in self.channels.values()]

        # set selected shapes
        for shape in shapes:
            shape.selected = shape.label in self.selected_channels

        # set shape's enabled
        for shape in shapes:
            shape.enabled = not self.is_channel_disabled(shape.label)

        app = get_app()
        app.window.displaymodel.add_shapes(shapes)

    def update_height_offset(self, height_offset: float):
        log.debug(f"updating channels height offset")
        for channel in self.channels.values():
            new_channel = channel
            new_channel.set_offset(height_offset)
            self.channels[channel.label] = new_channel
        self.update()

    def __init__(self):
        super().__init__()
        self.channels = {}
        self.diameter = NeedleChannel.default_diameter()
        self.selected_channels = []
        self.disabled_channels = []
        self.own_diameters: dict[str, float] = {}  # label: diameter that Apply on the Channels tab keeps
        config_values = get_app().values.config_values
        self.threading_depth = config_values.get("CONFIG_CHANNELS_THREADING_DEPTH")
        self.threading_diamenter = config_values.get("CONFIG_CHANNELS_THREADING_DIAMETER")

    @staticmethod
    def get_label(): return CHANNELS_LABEL
