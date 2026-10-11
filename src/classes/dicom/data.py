class DicomData:
    """
    Stores relevant data from a dicom dataset
    """

    def __init__(self):
        self.patient_name = None
        self.patient_id = None
        self.plan_label = None

        self.cylinder_roi = None
        self.cylinder_contour = None
        self.cylinder_tip = None
        self.cylinder_base = None
        self.cylinder_direction = None
        self.cylinder_diameter = None

        self.channels_rois = None
        self.channel_numbers = None
        self.channels_labels = None
        self.channel_contours = None
        self.channel_paths = None

        self.central_channel_roi = None
        self.central_axis_flag = None
        self.central_channel = None

        self.approval_status = None
        self.operator = None
        self.plan_ID = None

        self.tandem_channel = None
    '''
    def update(self, new_data):
        if new_data.patient_name:
            self.patient_name = new_data.patient_name

        if new_data.patient_id:
            self.patient_id = new_data.patient_id

        if new_data.plan_label:
            self.plan_label = new_data.plan_label

        if new_data.cylinder_roi:
            self.cylinder_roi = new_data.cylinder_roi

        if new_data.cylinder_contour:
            self.cylinder_contour = new_data.cylinder_contour

        if new_data.channels_rois:
            self.channels_rois = new_data.channels_rois

        if new_data.channel_contours:
            self.channel_contours = new_data.channel_contours
    
     '''
    #note if any value is added to __init__ it will also have to be added to here so that it is reset after an import 
    def reset(self):
        self.patient_name = None
        self.patient_id = None
        self.plan_label = None

        self.cylinder_roi = None
        self.cylinder_contour = None
        self.cylinder_tip = None
        self.cylinder_base = None
        self.cylinder_direction = None
        self.cylinder_diameter = None

        self.channels_rois = None
        self.channel_numbers = None
        self.channels_labels = None
        self.channel_contours = None
        self.channel_paths = None

        self.central_channel_roi = None
        self.central_axis_flag = None
        self.central_channel = None

        self.approval_status = None
        self.operator = None
        self.plan_ID = None

        self.tandem_channel = None #stores the name of the tandem channel

    def toString(self):
        text = "## DicomData Object:\n"
        text += f"Patient {self.patient_name} -- ID: {self.patient_id}\n"

        if self.cylinder_roi:
            text += f"Cylinder ROI Number {self.cylinder_roi}\n"
        else:
            text += ""

        if self.channels_rois:
            text += f"\nChannels ({len(self.channels_rois)} loaded)\n"
            for i in range(len(self.channels_rois)):
                text += f" Channel {self.channels_rois[i]}\n"
        else:
            text += "\nNo Channel Data!\n"

        return text
