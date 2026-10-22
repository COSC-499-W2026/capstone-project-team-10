from PySide6.QtCore import QObject, Signal

from .shape_model import ShapeModel, ShapeTypes
from classes.app import get_app
from classes.logger import log

default_colours = {
    ShapeTypes.CYLINDER:    [1.0, 1.0, 1.0],
    ShapeTypes.CHANNEL:     [0.2, 0.55, 0.55],
    ShapeTypes.TANDEM:      [1.0, 1.0, 1.0],
    ShapeTypes.SELECTED:    [0.2, 0.55, 0.55], 
    ShapeTypes.EXPORT:      [0.8, 0.0, 0.0]}

default_materials = {
    ShapeTypes.CYLINDER: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.CHANNEL: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.TANDEM: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.SELECTED: {"rgb": [0.2, 0.55, 0.55], "transparent": True}
}


class DisplayModel(QObject):

    shapes_changed = Signal(list, bool)
    reset_completed = Signal()

    def add_shape(self, shape: ShapeModel):
        log.debug(f"adding {shape.label}")
        if not shape.enabled: del self.shapes[shape.label]
        else: self.shapes[shape.label] = shape
        log.debug(f"Shapes: {self.shapes.keys()}")

    def add_shapes(self, shapes:list):
        log.debug(f"adding {[shape.label for shape in shapes]}")
        for shape in shapes:
            if not shape.enabled:  # if disabled, remove the shape all together 
                if shape.label in self.shapes:
                    del self.shapes[shape.label]
            else: self.shapes[shape.label] = shape
        log.debug(f"Shapes: {self.shapes.keys()}")

    def remove_shape(self, label:str):
        log.debug(f"removing {label}")
        if label in self.shapes:
            self.shapes.pop(label)

    def remove_shapes(self, labels:list):
        log.debug(f"removing {labels}")
        for label in labels:
            self.shapes.pop(label)

    def set_materials(self, materials: dict) -> None:
        log.debug(f"updating materials list to: {materials}")
        self.materials = materials

    def set_selected_shapes(self, shapes):
        log.debug(f"selecting {shapes} \n\n{shapes[0].DumpJsonToString()}")
        label = ""

        # each shape is set to not selected 
        # then set to selected if found
        for label, old_shape in self.shapes.items():
            self.shapes[label].selected = False  # if not found, stay False
            if shapes[0].IsEqual(old_shape.shape):
                self.shapes[old_shape.label].selected = True
                continue

        log.debug(f"shape matches {label}")

    def set_shape_colour(self, colours: dict):
        """
        colours is {ShapeTypes: [0.5, 0.5, 0.5]}
        """
        self.colours = colours

    def set_shape_visibility(self, visibility: dict):
        """
        visibility is {label: bool} where True means the shape is passed to the display
        """
        self.visibility.update(visibility)

    def set_transparent(self, is_transparent:bool):
        for label in self.shapes:
            self.shapes[label].transparent = is_transparent

    def show_shape(self, shape: ShapeModel):
        """
        Override settings to show only a single shape model
        """
        self.shapes_changed.emit([shape], True)

    def show_shapes(self, shapes: list[ShapeModel]):
        self.shapes_changed.emit(shapes, True)

    def update(self):
        """
        To update the viewport's shapes
        """
        shapes = self.shapes.values()
        # colour remaining shapes
        for shape in shapes:
            shape_type = shape.type
            if shape.selected: shape_type = ShapeTypes.SELECTED

            shape.material = self.materials[shape_type]
        self.shapes_changed.emit(list(shapes), True)

    def reset(self):
        self.visibility = {}  # label: bool where True is visible
        self.shapes = {}  # each entry stored as (ShapeModel)
        self.reset_completed.emit()
        self.shapes_changed.emit([], False)

    def __init__(self):
        super().__init__()
        self.colours = default_colours
        self.materials = default_materials
        self.visibility = {}  # label: bool where True is visible
        self.shapes = {}  # each entry stored as (ShapeModel)

        # signals and slots
        # connected under initViews() in MainWindow class
