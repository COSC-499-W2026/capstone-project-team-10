from PySide6.QtWidgets import QFileDialog, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QColor, QIcon, QPixmap

from classes.app import get_app
from classes.logger import log
from classes.dicom.fileio import read_dicom_folder
from classes.dicom.structure_list import structure_list_rows
from windows.models.shape_model import ShapeTypes
from windows.ui.import_view_ui import Ui_Import_View
from windows.views.custom_view import display_action, CustomView

from settings.load import load_config_file
from settings.reset import resetAllValues


materials = {
    ShapeTypes.CYLINDER: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.CHANNEL: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.TANDEM: {"rgb": [0.2, 0.55, 0.55], "transparent": True},
    ShapeTypes.SELECTED: {"rgb": [0.2, 0.55, 0.55], "transparent": True}
}


class ImportView(CustomView):

    def action_import_config_file(self):

        file_name = QFileDialog.getOpenFileName(
            self, "Open config file", "", "(*.json)")[0]
        
        # if no .json file is selected, then return (cancel the import)
        if file_name == "": 
            """
              NOTE: the other action_import_* methods below return '' if user presses cancel, since they are 
              expecting a string.  This is why if not foldername: works for those, but it doesn't for here.
            """
            log.info("no valid filename selected for importing")
            return

        # if a .json file has been selected
        log.info(f"file {file_name} has been selected")


        app = get_app()
        # get the current values in use.
        alternate_dict = app.values.config_values
        # read in the file and store the values.
        # read the default settings from the .json file, as a dictionary,
        # and store it in an attribtue called config_values so it can be accessed later.
        load_config_file_tuple = load_config_file(file_name=file_name, 
                                                  alternate_dict=alternate_dict,
                                                  num_configs_loaded_successfully=app.values.num_configs_loaded_successfully)
        app.values.config_values = load_config_file_tuple[0]
        # store the list of which config values were successfully loaded or not.
        app.values.config_keys_loaded = load_config_file_tuple[1]
        # store the count of how many config files were "successful".
        # "successful" means 1 or more values were loaded from it.
        app.values.num_configs_loaded_successfully = load_config_file_tuple[2]

        # update the config label on the import view to display the info from the loaded config file.   
        app.values.loaded_message = app.values.createConfigMessageText(file_name, isFromUserImport=True)
        self.action_update_import_label()
        #The tandems length should not be larger than the cylinder
        max_tandem_len = app.values.config_values.get('CONFIG_CYLINDER_LENGTH')
        app.window.navigationmodel.views[3].ui.sb_tandem_height.setMaximum(max_tandem_len)

        # reset all the values in the spin boxes and in the views.
        resetAllValues(app.values.config_values)

        app.values.most_recently_opened_config_file = file_name

        log.info("Successfully reset all the values and views.")


    def action_import_dicom_folder(self, folder=None):
        if folder==None:
            foldername = QFileDialog.getExistingDirectoryUrl(
                self, "Open patient folder").toLocalFile()
        else: # if a folder is specified to open to
            foldername = QFileDialog.getExistingDirectory(
                self, "Open patient folder",
                dir=folder)

        if not foldername:  # no folder selected?
            log.info("no valid filename selected for importing")
            return

        self.import_dicom_from_folder(foldername)

    def import_dicom_from_folder(self, foldername: str) -> None:
        """Load a DICOM plan from a known folder path (no folder dialog)."""
        self.folder_name = foldername

        app = get_app()
        window = app.window

        log.info(f"file {foldername} has been selected")

        # record the current cylinder length.
        # This value is always compared against when the cylinder length changes.
        cylindermodel = app.window.cylindermodel
        cylindermodel.starting_length = app.values.config_values.get("CONFIG_CYLINDER_LENGTH")
        
        # for an imported tandem:
        # place the bottom of the original imported shape at the origin (0,0,0) (the base of the cylinder)
        # reset the tandem height_offset to 0 when a new dicom file is loaded.
        tandemmodel = app.window.tandemmodel
        tandemmodel.height_offset = 0.0
        # set the mesh_offset to 0 and reset the spin box to 0.
        tandemmodel.mesh_offset = 0.0
        window.navigationmodel.views[3].ui.sb_height_offset.setValue(0.0)
        #sets the fact a tandem is in the plan to False
        window.navigationmodel.views[3].hasShownRotationWarning = False
        tandemmodel.hasTandemInDICOM = False

        try:
            data = window.dicommodel.data.reset() # resets all the data in the dicom 
            window.displaymodel.reset() # resets all the data in the display
        except:
            log.error("Error: Unable to reset screen properly")
        try:
            data = read_dicom_folder(foldername)
        except:
            log.error("Empty folder selected.")
            self.action_update_structure_list()
            return

        # Add patient and plan info to window

        #this must be imported here rather than at the top with the other imports or the import will be called prior to method_found being determined and the wrong value will be used
        from classes.dicom.fileio import method_found

        if(method_found):
            window.dicommodel.update(data)
            window.displaymodel.set_transparent(True)

            self.action_update_import_label()
            self.action_update_structure_list()
            window.navigationmodel.views[2].create_channels_list()#updates channels list
            #The tandems length should not be larger than the cylinder
            max_tandem_len = app.values.config_values.get('CONFIG_CYLINDER_LENGTH')
            app.window.navigationmodel.views[3].ui.sb_tandem_height.setMaximum(max_tandem_len)
            
            app.signals.viewChanged.emit(4)
            window.change_color_export()
        else:
            self.action_update_structure_list()

    def action_update_import_label(self):
        self.ui.info_area.clear()

        app = get_app()

        if(app.window.dicommodel.data.patient_id):
            data = get_app().window.dicommodel.data
            alldata= "Folder: "+self.folder_name+"\n\nPatient and Plan Info\n"
            a = ("Patient ID:         \t")          + str(data.patient_id)+ "\n"
            b = ("Patient Name:    \t")          + str(data.patient_name)+ "\n"
            c = ("Plan ID:                \t")          + str(data.plan_label)+ "\n"
            d = ("Approval Status: \t")          + str(data.approval_status) + "\n"
            e = ("Operator:           \t")          + str(data.operator) + "\n\n"
            f = ("Channels Info")                  + "\n"
            for i in range(len(data.channels_labels)):
                f = f+(str(data.channels_labels[i]))+ ",  Channel: "+str(data.channel_numbers[i])+"\n"
            

            tandem = data.tandem_channel
            g = ("Tandem Label:  ")+str(tandem)
            
            alldata = alldata+a+b+c+d+e+f+g+'\n\n'

            #self.ui.info_area.append(alldata)
            self.ui.info_area.append(alldata)


        """
        Updates the config label on the Import view to display the file name of the current config file.
        If no config file was loaded, or if no values from it were used, then display "None".
        """
        self.ui.info_area.append(app.values.loaded_message)

    def action_update_config_label(self, file_name):
        print("")

    def action_update_structure_list(self):
        """Show ROI visibility controls and explain unavailable contours."""
        model = get_app().window.structuresmodel
        structures = tuple(model.structures.values())
        with QSignalBlocker(self.structure_list):
            self.structure_list.clear()
            for structure, row in zip(structures, structure_list_rows(structures)):
                item = QListWidgetItem(f"{row.label}  {row.category}")
                roi = structure.roi_number
                item.setData(Qt.UserRole, roi)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if roi in model.visible else Qt.Unchecked)
                reason = model.unavailable.get(roi)
                if reason:
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                    item.setToolTip(reason)
                else:
                    item.setToolTip("Show or hide this DICOM contour outline")
                swatch = QPixmap(12, 12)
                swatch.fill(QColor(*row.color))
                item.setIcon(QIcon(swatch))
                self.structure_list.addItem(item)

    def action_toggle_structure(self, item: QListWidgetItem):
        """Keep anatomy visibility separate from printable shapes."""
        get_app().window.structuresmodel.set_visible(
            item.data(Qt.UserRole), item.checkState() == Qt.Checked)

    @display_action
    def on_open(self):
        log.debug(f"on view open")
        displaymodel = get_app().window.displaymodel
        displaymodel.set_materials(materials)

    def __init__(self):
        self.folder_name = ""
        super().__init__()
        self.ui = Ui_Import_View()
        self.ui.setupUi(self)

        self.structure_list = QListWidget(self)
        self.structure_list.setObjectName("structure_list")
        self.structure_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        # Match info_area: page_import sets near-white text that would hide list labels.
        self.structure_list.setStyleSheet(
            "background-color: rgb(255, 255, 255); color: rgb(0, 0, 0);"
        )
        self.ui.verticalLayout_3.addWidget(self.structure_list)

        # signals and slots
        self.structure_list.itemChanged.connect(self.action_toggle_structure)
        get_app().window.structuresmodel.changed.connect(self.action_update_structure_list)
        self.ui.btn_import_folder.pressed.connect(self.action_import_dicom_folder)
        self.ui.btn_config_file.pressed.connect(self.action_import_config_file)
