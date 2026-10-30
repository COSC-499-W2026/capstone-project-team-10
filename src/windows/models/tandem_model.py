from OCC.Core.gp import gp, gp_Vec
from OCC.Extend.ShapeFactory import translate_shp, rotate_shape

from PySide6.QtCore import QObject, Signal

from classes.app import get_app
from classes.logger import log
from classes.mesh.channel import NeedleChannel
from classes.mesh.fileio import read_3d_file
from classes.mesh.helper import extend_bottom_face
from classes.mesh.tandem import Tandem
from windows.models.shape_model import ShapeModel, ShapeTypes

TANDEM_LABEL = "tandem_shape"


class TandemModel(QObject):

    values_changed = Signal()

    def exists(self):
        # Returns True if the tandem has a _base_shape (ie, if there is a tandem currently in use, both generated or imported).
        # Returns False if the tandem does not have a _base_shape (ie, if there is no tandem currently in use).
        if self._base_shape is None:
            return False
        else:
            return True

    def clear_tandem(self):
        # remove tandem from the display
        self._base_shape = None
        self.filepath = None
        self.update()

    def import_tandem(self, filepath: str):
        self.filepath = filepath
        self._base_shape = read_3d_file(filepath)
        self.is_shape_imported = True
        self.update()

    def set_import_height_offset(self, height_offset: float):
        if self.mesh_offset == height_offset:
            return
        if not self.filepath:
            # if we have not imported a tandem yet, then do not offset height.
            # ie. cannot offset height of generated tandem, bc instead use "tandem height" under "generate" tab
            return

        self.mesh_offset = height_offset
        # tandem_length is the length of the tandem itself plus the offset
        config_values = get_app().values.config_values
        self.tandem_length = config_values.get("CONFIG_TANDEM_TIP_HEIGHT") + height_offset
        self.update()

    def set_tandem(self):

        log.debug(f"setting tandem")
        self.filepath = None
        self.is_shape_imported = False  # used to flag height offsets

        self._generate_tandem()

        self._display_shape = self.raw_shape()

        self.update()

    def set_tandem_channel(self, channel: NeedleChannel | None):
        # with no tandem channel the tandem keeps the rotation it has
        if channel is None: return
        self.rotation = channel.get_rotation()
        if(channel.label.lower() == 'tandem'):
            self.protation = self.rotation
            self.hasTandemInDICOM = True # if this happens there is a tandem in the plan
        self.update_display()

    def change_tandem_rotation(self, rotation):
        self.rotation = rotation
        #try and except added to ensure rotation and spin boxes are updated accuratly
        try:
            self._display_shape = rotate_shape(shape=self._base_shape, axis=gp.OZ(), angle=rotation)
            self.update()
        except:
            pass

    def shape(self):
        if not self._base_shape:
            return None
        log.debug(f"shape offsets being applied")

        # if using an imported file, also apply the mesh's offset
        height_offset = self.height_offset
        if self.filepath:
            height_offset += self.mesh_offset

        # apply offsets
        offset = gp_Vec(0.0, 0.0, height_offset)
        rotation = self.rotation

        shape = rotate_shape(
            shape=self._base_shape, axis=gp.OZ(), angle=rotation)
        if self.is_shape_imported:
            shape = translate_shp(shape, offset)

        if self.filepath:
            shape = extend_bottom_face(shape)

        return shape

    def raw_shape(self):
        log.debug(f"display shape being generated")
        tandem = Tandem()

        tandem.tandem_diameter = self.tandem_diameter
        tandem.stopper_diameter = self.stopper_diameter
        tandem.tandem_angle = self.tip_angle
        tandem.bend_radius = self.bend_radius
        tandem.tandem_height = self.tandem_length

        tandem.cylinder_height = self.cylinder_length
        tandem.cylinder_diameter = self.cylinder_diameter

        rotation = self.rotation

        self._display_shape = rotate_shape(shape=tandem.tandem_shape(), axis=gp.OZ(), angle=rotation)
        return self._display_shape

    def update(self):
        log.debug(f"updating")
        self.values_changed.emit()
        self.update_display()

    def update_cylinder(self):
        log.debug("updating cylinder on tandem model")

        cylindermodel = get_app().window.cylindermodel
        self.cylinder_length = cylindermodel.cylinder.length
        self.cylinder_diameter = cylindermodel.cylinder.diameter

        if self._base_shape is None:
            return

        if not self.is_shape_imported:
            self._generate_tandem()

        self.update()

    def update_display(self):
        log.debug(f"update display")
        if not self._base_shape:
            self.displaymodel.remove_shape(TANDEM_LABEL)
            return

        shape = self.shape()
        if not shape:
            return

        shape_model = ShapeModel(
            label=TANDEM_LABEL, shape=shape, shape_type=ShapeTypes.TANDEM)

        self.displaymodel.add_shape(shape_model)

    def update_height_offset(self, height_offset: float):
        # here, height_offset refers to the amount that the tandem is adjusted vertically to remain
        # aligned with the cylinder when the cylinder height changes.
        # not to be confused with the height offset spin box (whose value is stored as self.mesh_offset)
        log.debug(f"updating tandem height offset to {height_offset}")
        self.height_offset = height_offset
        self.update()

    def _generate_tandem(self):
        tandem = Tandem()


        errors = []
        """
        Algorithm:
        1. For each spin box value, try to generate a new tandem with the new values up to that point.
        2. If there is NO error in the tandem generation, then: 
            a. set the spin box to the new value.
        3. If there IS an error in the tandem generation, then:
            a. this means that the values in "shape" are from the ones that have already been successfully applied, 
                but not the current one that generated the error.  So the view will not display a shape with the 
                erroneous value.
            b. record the name of the value that caused the error in the errors list.
            c. change the spin box back to the previous value.
            d. keep self.*(value_name) as the ERRONEOUS value, to continue down the list and try to generate
                the tandem with the further new values.  It may be that one of the later values will fix the problem.
        4. After generating a tandem for each new value, if there are NO errors remaining in the list:
            a. use the final shape to update _base_shape().  You are happy.
        5. After generating a tandem for each new value, if there ARE errors remaining:
            a. for each erroneous value, set self.*(value_name) back to the previous value, 
                since it is not used in the current "shape".
            b. call a pop-up message to alert the user to which values were erroneous.
        """
        # store a copy of the previous values in case there are errors.
        # if there are errors, we will reset back to previous values.
        previous_tandem = Tandem()

        tandemUI = get_app().window.navigationmodel.views[3].ui
        
        tandem.threading_depth = self.threading_depth
        tandem.threading_diameter = self.threading_diameter
        tandem.cylinder_height = self.cylinder_length
        tandem.cylinder_diameter = self.cylinder_diameter
        
        try:
            temp = tandem.tandem_diameter
            tandem.tandem_diameter = self.tandem_diameter
            shape = tandem.generate_shape()
            tandemUI.sp_channel_diameter.setValue(self.tandem_diameter)
        except Exception as e:
            errors.append("diam")
            tandemUI.sp_channel_diameter.setValue(temp)
            log.debug(e)
        try:
            temp = tandem.stopper_diameter
            tandem.stopper_diameter = self.stopper_diameter
            shape = tandem.generate_shape()
            tandemUI.sp_stopper_diameter.setValue(self.stopper_diameter)
        except Exception as e:
            errors.append("stopper")
            tandemUI.sp_stopper_diameter.setValue(temp)
            log.debug(e)
        try:
            temp = tandem.tandem_angle
            tandem.tandem_angle = self.tip_angle
            shape = tandem.generate_shape()
            tandemUI.sp_bend_angle.setValue(self.tip_angle)
        except Exception as e:
            errors.append("angle")
            tandemUI.sp_bend_angle.setValue(temp)
            log.debug(e)
        try:
            temp = tandem.bend_radius
            tandem.bend_radius = self.bend_radius
            shape = tandem.generate_shape()
            tandemUI.sb_bend_radius.setValue(self.bend_radius)
        except Exception as e:
            errors.append("radius")
            tandemUI.sb_bend_radius.setValue(temp)
            log.debug(e)
        try:
            temp = tandem.tandem_height
            tandem.tandem_height = self.tandem_length
            shape = tandem.generate_shape()
            tandemUI.sb_tandem_height.setValue(self.tandem_length)
            # if the above did not generate errors, then this means that there is no error in the final tandem.
            # So, set errors list to empty.
            if(len(errors)>=1):
                errors = []
        except Exception as e:
            errors.append("height")
            tandemUI.sb_tandem_height.setValue(temp)
            log.debug(e)
        
        # if there are remaining errors with a particular value, set values to previous values, 
        # since shape is now built with the previous values, not the erroneus, new values.
        for code in errors:
            if(code == 'diam'):
                self.tandem_diameter = previous_tandem.tandem_diameter

            elif(code == 'stopper'):
                self.stopper_diameter = previous_tandem.stopper_diameter

            elif(code == 'angle'):
                self.tip_angle = previous_tandem.tandem_angle

            elif(code == 'height'):
                self.tandem_length = previous_tandem.tandem_height

            elif(code == 'radius'):
                self.bend_radius = previous_tandem.bend_radius

        if(len(errors)>0):
            for err in errors:
                get_app().window.tandem_error(err)

        self._base_shape = shape

    def __init__(self) -> None:
        super().__init__()
        config_values = get_app().values.config_values
        self._base_shape = None  # base shape before extending due to height offset
        self._display_shape = None  # used to show tandem in export view
        self.height_offset = 0.0 # amount adjusted when cylinder height is changed
        self.rotation = config_values.get("CONFIG_TANDEM_ROTATION") 
        self.protation = config_values.get("CONFIG_TANDEM_ROTATION") # "plan rotation"
        # This value is used when the user tries to generate or import a tandem using a (applied) spin box value
        # that does not equal the rotation value from their DICOM file or the config file.
        # If there is a channel labeled "tandem" in the DICOM file, this stores the rotation from that channel.
        # If there is no channel labeled "tandem" in the DICOM file, this stores the config value for rotation.
        # TODO this could be used to add a "reset tandem to plan" button.
        self.filepath = None
        self.mesh_offset = 0.0 # amount adjusted when user applies "height offset" spin box
        self.is_shape_imported = False
        self.threading_diameter = config_values.get("CONFIG_TANDEM_THREADING_DIAMETER")
        self.threading_depth = config_values.get("CONFIG_TANDEM_THREADING_DEPTH")

        # cylinder settings
        self.cylinder_length = 0
        self.cylinder_radius = 0

        # tandem settings
        self.tandem_diameter = config_values.get("CONFIG_TANDEM_CHANNEL_DIAMETER")
        self.stopper_diameter = config_values.get("CONFIG_TANDEM_STOPPER_DIAMETER")
        self.tandem_angle = config_values.get("CONFIG_TANDEM_TIP_ANGLE")
        self.bend_radius = config_values.get("CONFIG_TANDEM_BEND_RADIUS")
        self.tandem_length = config_values.get("CONFIG_TANDEM_TIP_HEIGHT")
        self.hasTandemInDICOM = False # this value will be set to True in the event there is a channel labeled tandem

        # generated tandem settings
        self.tip_angle = config_values.get("CONFIG_TANDEM_TIP_ANGLE")

        # signals and slots
        window = get_app().window
        window.channelsmodel.tandem_changed.connect(self.set_tandem_channel)
        window.cylindermodel.values_changed.connect(self.update_cylinder)

        # references
        self.displaymodel = window.displaymodel

    @staticmethod
    def get_label(): return TANDEM_LABEL
