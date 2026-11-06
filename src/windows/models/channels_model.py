from dataclasses import replace
from enum import Enum, auto
from math import isfinite

from PySide6.QtCore import QObject, Signal

from classes.app import get_app
from classes.dicom.data import DicomData
from classes.logger import log
from classes.mesh.channel import NeedleChannel
from classes.mesh.helper import CustomNeedleError, CustomNeedleSpec, custom_needle_points, cut_is_clean
from settings.defaults import MINIMUM_CHANNEL_DIAMETER_MM
from windows.models.shape_model import ShapeModel, ShapeTypes

CHANNELS_LABEL = "applicator_"
CUSTOM_LABEL = "Custom Applicator"


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
        self.custom_specs = {}
        self.height_offset = 0.0  # a new plan starts at its own cylinder length
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

    def has_plan(self) -> bool:
        return get_app().window.dicommodel.data.channel_paths is not None

    def next_custom_label(self) -> str:
        """The first Custom Applicator name, counting from 1, that no channel has."""
        number = 1
        while f"{CUSTOM_LABEL}{number}" in self.channels:
            number += 1
        return f"{CUSTOM_LABEL}{number}"

    def is_custom_needle(self, label: str) -> bool:
        return label in self.custom_specs

    def check_custom_needle(self, spec: CustomNeedleSpec, editing: str = "") -> list[list[float]]:
        """The points of a custom needle in the plan's frame, or CustomNeedleError saying which rule it breaks.

        When editing, the applicator being edited may keep its own name.
        """
        if not self.has_plan():
            raise CustomNeedleError("Import a plan before adding an applicator")
        label = spec.label.strip()
        if not label:
            raise CustomNeedleError("Name the applicator")
        if label in self.channels and label != editing:
            raise CustomNeedleError(f"An applicator named {label} already exists")
        cylinder = get_app().window.cylindermodel.cylinder
        points = custom_needle_points(spec, cylinder.diameter, cylinder.length, self.diameter)
        points = [[x, y, z - self.height_offset] for x, y, z in points]  # get_points adds the offset back
        if not cut_is_clean(cylinder.shape(), self.make_custom_needle(replace(spec, label=label), points, "0").shape()):
            raise CustomNeedleError("The cylinder cannot be cut cleanly at these numbers, so change the start, a length or Phi a little")
        return points

    def custom_needle_error(self, spec: CustomNeedleSpec, editing: str = "") -> str:
        """The reason a spec is refused, or an empty string when it would be added or, when editing, applied."""
        try:
            self.check_custom_needle(spec, editing)
        except CustomNeedleError as error:
            return str(error)
        return ""

    def make_custom_needle(self, spec: CustomNeedleSpec, points: list[list[float]], channel_number: str) -> NeedleChannel:
        needle = NeedleChannel(roi_number="custom", channel_number=channel_number, label=spec.label, points=points)
        needle.set_diameter(self.own_diameters.get(spec.label, self.diameter))
        needle.set_offset(self.height_offset)
        return needle

    def add_custom_needle(self, spec: CustomNeedleSpec) -> NeedleChannel:
        points = self.check_custom_needle(spec)
        spec = replace(spec, label=spec.label.strip())
        numbers = [int(channel.channel_number) for channel in self.channels.values() if channel.channel_number.isdigit()]
        needle = self.make_custom_needle(spec, points, str(max(numbers, default=0) + 1))
        self.channels[spec.label] = needle
        self.custom_specs[spec.label] = spec
        log.info(f"added custom applicator {spec.label} starting at ({spec.x}, {spec.y}) mm")
        self.update()
        return needle

    def require_custom_needle(self, label: str) -> None:
        if not self.is_custom_needle(label):
            raise CustomNeedleError("Only a custom applicator can be edited or removed")

    def rename_channel(self, label: str, new_label: str) -> None:
        """Move a label to a new name in every record that keys on it, keeping the list place."""
        if new_label == label: return
        self.channels = {(new_label if name == label else name): channel for name, channel in self.channels.items()}
        self.custom_specs = {(new_label if name == label else name): spec for name, spec in self.custom_specs.items()}
        self.own_diameters = {(new_label if name == label else name): diameter for name, diameter in self.own_diameters.items()}
        self.disabled_channels = [new_label if name == label else name for name in self.disabled_channels]
        self.selected_channels = [new_label if name == label else name for name in self.selected_channels]
        data = get_app().window.dicommodel.data
        if data.tandem_channel == label: data.tandem_channel = new_label
        get_app().window.displaymodel.remove_shape(label)  # add_shapes never drops a shape, so the old name would still be drawn

    def edit_custom_needle(self, label: str, spec: CustomNeedleSpec) -> NeedleChannel:
        """Rebuild a custom applicator from new numbers and a new name, keeping its number, place, diameter, disabled state and move."""
        self.require_custom_needle(label)
        spec = replace(spec, label=spec.label.strip())
        points = self.check_custom_needle(spec, editing=label)
        old = self.channels[label]
        self.rename_channel(label, spec.label)
        needle = self.make_custom_needle(spec, points, old.channel_number)
        needle.set_translation(old.translation)
        self.channels[spec.label] = needle
        self.custom_specs[spec.label] = spec
        log.info(f"edited custom applicator {label} into {spec.label}, now starting at ({spec.x}, {spec.y}) mm")
        self.update()
        return needle

    def remove_channel(self, label: str) -> None:
        """Delete an applicator, plan or custom, and every record of its label. The tandem is refused, and a plan comes back only by importing again."""
        if label not in self.channels:
            raise KeyError(label)
        if self.is_channel_tandem(label):
            raise CustomNeedleError("Choose another tandem before removing the applicator that is the tandem")
        del self.channels[label]
        get_app().window.displaymodel.remove_shape(label)  # add_shapes never drops a shape, so a removed one would still be drawn
        self.custom_specs.pop(label, None)
        self.own_diameters.pop(label, None)
        self.disabled_channels = [disabled for disabled in self.disabled_channels if disabled != label]
        self.selected_channels = [selected for selected in self.selected_channels if selected != label]
        log.info(f"removed applicator {label}")
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
        if label and not label in self.disabled_channels:
            self.disabled_channels.append(label)
        # the tandem channel leaves the Channels list, so it cannot stay selected there
        if label and label in self.selected_channels:
            self.selected_channels = []

        self.update()
        self.tandem_changed.emit(self.get_tandem_channel())

    def toggle_channel_enabled(self, label: str):
        log.debug(f"Toggling channel enable")
        if self.is_channel_tandem(label):
            raise ValueError(f"{label} is the tandem channel and is never cut as a needle")
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
        self.height_offset = height_offset
        for channel in self.channels.values():
            new_channel = channel
            new_channel.set_offset(height_offset)
            self.channels[channel.label] = new_channel
        self.update()

    def __init__(self):
        super().__init__()
        self.channels = {}
        self.height_offset = 0.0  # how far the cylinder is from its length at import, which the channels follow
        self.diameter = NeedleChannel.default_diameter()
        self.selected_channels = []
        self.disabled_channels = []
        self.own_diameters: dict[str, float] = {}  # label: diameter that Apply on the Channels tab keeps
        self.custom_specs: dict[str, CustomNeedleSpec] = {}  # label: the numbers a custom applicator was built from
        config_values = get_app().values.config_values
        self.threading_depth = config_values.get("CONFIG_CHANNELS_THREADING_DEPTH")
        self.threading_diamenter = config_values.get("CONFIG_CHANNELS_THREADING_DIAMETER")

    @staticmethod
    def get_label(): return CHANNELS_LABEL
