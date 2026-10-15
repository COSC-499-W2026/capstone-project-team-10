import numpy as np
from pathlib import Path
import pydicom
from classes.logger import log
from classes.dicom.data import DicomData
from classes.dicom.load_structures import load_structures
from classes.mesh.cylinder import BrachyCylinder
from classes.mesh.channel import NeedleChannel
import classes.mesh.helper as helper
from classes.app import get_app
global method_found
method_found = False

def get_cylinder_from_dicom(data: DicomData) -> BrachyCylinder: 
    diameter = data.cylinder_diameter
    tip = data.cylinder_tip
    base = data.cylinder_base

    log.debug(f"Cylinder results: \n Diameter: {diameter}\n Tip: {tip}\n Base: {base}")
    return BrachyCylinder(tip=tip, base=base, diameter=diameter)


def is_rp_file(filepath: str) -> bool:
    """Checks if a file is a RTPLAN DICOM file and if it contains the data for needle channels"""
    try:
        dataset = pydicom.dcmread(filepath)

        if dataset.Modality != 'RTPLAN': return False

        # finding the contour data
        channels = dataset.ApplicationSetupSequence[0].ChannelSequence
        if len(channels) < 1:
            return False
    except Exception as error_message:
        log.info(f"Error reading RP DICOM file: {filepath} \n{error_message}")
        return False
    else:
        return True


def is_rs_file(filepath: str) -> bool:
    """Checks if a file is a RTSTRUCT DICOM file and if it contains the data to make a cylinder"""
    try:
        dataset = pydicom.dcmread(filepath)

        if dataset.Modality != 'RTSTRUCT': return False


    except Exception as error_message:
        log.info(f"Error reading dicom file: {filepath}\n{error_message}")
        return False

    return True


def load_central_axis_varian(data: DicomData, rs_dataset):

    for sequence in rs_dataset.ROIContourSequence:
        if sequence.ReferencedROINumber == data.central_channel_roi:
            central_channel = sequence
            break

    channel_contour_raw = central_channel.ContourSequence[0].ContourData
    points = [channel_contour_raw[i:i + 3] for i in range(0, len(channel_contour_raw), 3)]
    data.central_channel = points

    data.cylinder_tip = np.asarray(data.central_channel[0])
    data.cylinder_base = np.asarray(data.central_channel[-1])
    config_values = get_app().values.config_values
    data.cylinder_diameter = config_values.get("CONFIG_CYLINDER_DIAMETER")
    data.cylinder_direction = data.cylinder_tip - data.cylinder_base   

def load_central_axis_nucletron(data: DicomData, channels_data):
    central_channel = None
    # central_channel = rp_dataset.ApplicationSetupSequence[0].ChannelSequence[data.central_channel_roi].BrachyControlPointSequence
    for contoursequence in channels_data[0].ROIContourSequence:
        if data.central_channel_roi == int(contoursequence.ReferencedROINumber):
            central_channel = contoursequence.ContourSequence[0].ContourData
            break
    if central_channel is None:
        log.info(f"No central channel contour sequence found corresponding to central channel: {data.central_channel_roi}")
        return

    
    central_channel_points = [central_channel[i:i+3] for i in range(0, len(central_channel), 3)] 
    data.central_channel = central_channel_points

    data.cylinder_tip = np.asarray(data.central_channel[0])
    data.cylinder_base = np.asarray(data.central_channel[-1])
    config_values = get_app().values.config_values
    data.cylinder_diameter = config_values.get("CONFIG_CYLINDER_DIAMETER")
    data.cylinder_direction = data.cylinder_tip - data.cylinder_base   


def load_channels_varian(data: DicomData, rs_dataset):
    channel_contours = list(filter(lambda sequence: (sequence.ReferencedROINumber in data.channels_rois),
                                    rs_dataset.ROIContourSequence))
    # Note: the above list has the points in order of ascending ROI number.
    # In contrast, the data.channels_rois, data.channel_numbers, and data.channels_labels lists have the 
    # data stored in order of ascending channel number.
    # Hence, the channel_contours list does not align with the other 3 data.channels_* lists; it is out of order.
    # The below for loop fixes this so that all the lists are aligned.

    ordered_channel_contours = []
    # Align the channels_counters data so the ROIs match the order in data.channels_rois
    for item in data.channels_rois:
        roi = int(item)
        for i, channel in enumerate(channel_contours):
            if int(channel.ReferencedROINumber) == roi:
                ordered_channel_contours.append(channel)


    # channel points are a single array dividable by 3
    # so for each channel, take those three points and put them into a small 3 list
    channel_contour_points = []
    for channel in ordered_channel_contours:
        points = [[
            channel.ContourSequence[0].ContourData[i],
            channel.ContourSequence[0].ContourData[i + 1],
            channel.ContourSequence[0].ContourData[i + 2]]
            for i in range(0, len(channel.ContourSequence[0].ContourData), 3)
        ]
        channel_contour_points.append(points)
    data.channel_contours = channel_contour_points

    channel_paths = []
    # use the brachy cylinder to offset the points
    # z axis reference, the direction we want the cylinder and needles to go
    z_up = np.array([0, 0, 1])
    base = data.cylinder_base  # transform offset
    cyl_vec = data.cylinder_direction  # rotation offset
    cyl_length = np.linalg.norm(cyl_vec)
    
    # normalized direction from tip to base
    config_values = get_app().values.config_values
    CONFIG_CYLINDER_LENGTH = config_values.get("CONFIG_CYLINDER_LENGTH")
    offset_vector = np.array([0, 0, - cyl_length + CONFIG_CYLINDER_LENGTH])

    anchor_points = 0
    updated_base = helper.rotate_points(base, cyl_vec, z_up)
    for i, c in enumerate(channel_contour_points):
        if(len(c)>1):
            new_points = np.array(c)
            new_points = helper.rotate_points(new_points, cyl_vec, z_up)
            new_points = np.array(new_points) - updated_base
            new_points = new_points + offset_vector
            channel_paths.append(list(list(points) for points in new_points))
        else:
            anchor_points += 1
            del data.channels_rois[i]
            # single points used as anchoring points do not always have labels or
            # channel numbers, if they do not then the length of the ROI list is longer than the
            # list of channel numbers and channel_labels, this will only work for if there is one
            # single point though since the user could potentially have one labeled anchoring point and
            # one unlabeled anchoring point
            if(len(data.channels_rois) != len(data.channel_numbers)):
                del data.channel_numbers[i]
            if(len(data.channels_rois) != len(data.channels_labels)):
                del data.channels_labels[i]
            # in the event of 2 anchoring points a warning is sent to the user asking them to ensure they
            # have not labeled either of their anchouring points to ensure all of the channeles are lined
            # up properly
            if(anchor_points==1):
                get_app().window.single_point_pop_up_Varian()
    data.channel_paths = channel_paths


def load_channels_nucletron(data: DicomData, channels_data, center_index):

    # Get the xyz values for each needle that isn't the central needle.
    rp_channels = channels_data[0].ROIContourSequence
    
    # Initialize a list to store the extracted ContourData
    channel_contours = []

    #loads all channels information in the order they are in the dicom, just as the ROI_Channels are loaded
    try:
        #if ContourData actually exists for the channel, then add it to the list of channel_contours, if not then add an empty list (since some channels are just anchor points with no contour data)   
        for channel in rp_channels:
            try:
                channel_contours.append(channel.ContourSequence[0].ContourData)
            except:
                # channel_contours.append([])
                continue     

        #removes central channel
        del channel_contours[center_index]

        # Reshape the contour_data into lists of lists with shape (n, 3) 
        for i, contour in enumerate(channel_contours):
            channel_contours[i] = [contour[i:i+3] for i in range(0, len(contour), 3)]
        
        for i in range(len(channel_contours)):
            for j in range(len(channel_contours[i])):
                for k in range(len(channel_contours[i][j])):
                    channel_contours[i][j][k] = float(channel_contours[i][j][k])
    except Exception as e:
        log.error("Failed to load channels due to: " + str(e))

    
    channel_paths = []
    # use the brachy cylinder to offset the points
    # z axis reference, the direction we want the cylinder and needles to go
    z_up = np.array([0, 0, 1])
    base = data.cylinder_base  # transform offset
    cyl_vec = data.cylinder_direction  # rotation offset
    cyl_length = np.linalg.norm(cyl_vec)
    
    # normalized direction from tip to base
    config_values = get_app().values.config_values
    CONFIG_CYLINDER_LENGTH = config_values.get("CONFIG_CYLINDER_LENGTH")
    offset_vector = np.array([0, 0, - cyl_length + CONFIG_CYLINDER_LENGTH])

    updated_base = helper.rotate_points(base, cyl_vec, z_up)
    anchor_points=0
    for i, c in enumerate(channel_contours):
        if(len(c)>1):
            new_points = np.array(c)
            new_points = helper.rotate_points(new_points, cyl_vec, z_up)
            new_points = np.array(new_points) - updated_base
            new_points = new_points + offset_vector
            channel_paths.append(list(list(points) for points in new_points))
        else:
            #ROI_singlton = data.channels_rois[i]
            del data.channels_rois[i]
            anchor_points+=1
            # single points used as anchoring points do not always have labels or
            # channel numbers, if they do not then the length of the ROI list is longer than the
            # list of channel numbers and channel_labels, this will only work for if there is one
            # single point though since the user could potentially have one labeled anchoring point and
            # one unlabeled anchoring point
            if(len(data.channels_rois) != len(data.channel_numbers)):
                del data.channel_numbers[i]
            if(len(data.channels_rois) != len(data.channels_labels)):
                del data.channels_labels[i]
            # in the event of 2 anchoring points a warning is sent to the user asking them to ensure they
            # have not labeled either of their anchouring points to ensure all of the channeles are lined
            # up properly
            #
            if(anchor_points==2):
                get_app().window.single_point_pop_up_Nucleatron()
    data.channel_paths = channel_paths


def load_cylinder_contour(data: DicomData, rs_dataset):
    data.cylinder_roi = list(filter(lambda s: ("surface" in s.ROIObservationLabel.lower()),
                                    rs_dataset.RTROIObservationsSequence))[0].ReferencedROINumber
    cylinder_contour = list(filter(lambda s: (s.ReferencedROINumber == data.cylinder_roi),
                                    rs_dataset.ROIContourSequence))[0]

    data.cylinder_contour = [[
        cylinder_contour.ContourSequence[0].ContourData[i],
        cylinder_contour.ContourSequence[0].ContourData[i + 1],
        cylinder_contour.ContourSequence[0].ContourData[i + 2]]
        for i in range(0, len(cylinder_contour.ContourSequence[0].ContourData), 3)]

    # cylinder offsets
    point1 = np.asarray(data.cylinder_contour[0])
    point2 = np.asarray(data.cylinder_contour[-1])
    difference = point2 - point1
    diameter = np.sqrt((difference[0]) ** 2 +
                    (difference[1]) ** 2 + (difference[2]) ** 2)
    data.cylinder_diameter = round(diameter, 1)

    middle_index = int(len(data.cylinder_contour) / 2)

    data.cylinder_tip = data.cylinder_contour[middle_index]
    data.cylinder_base = point1 + (difference / 2)
    data.cylinder_direction = data.cylinder_tip - data.cylinder_base   


def explore_rp_rs(rp_dataset, rs_dataset):
    # Test
    contours = []
    for contour in rs_dataset.ROIContourSequence[0].ContourSequence:
        contours.append(contour.ContourData)
    channel_contour_points_strings = []
    for channel in contours:
        points = [[
            channel[i],
            channel[i + 1],
            channel[i + 2]]
            for i in range(0, len(channel), 3)
        ]
        channel_contour_points_strings.append(points)

    import matplotlib.pyplot as plt
    # import numpy as np
    from mpl_toolkits.mplot3d import Axes3D

    list_of_lists_of_string_points = channel_contour_points_strings

    # Convert string lists to numpy arrays of floats
    list_of_numeric_arrays = []
    for sublist in list_of_lists_of_string_points:
        numeric_sublist = [np.array(point, dtype=float) for point in sublist]
        list_of_numeric_arrays.append(np.array(numeric_sublist))

    # Create a 3D plot
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Colors and markers for each array
    colors = ['r', 'g', 'b', 'r', 'g', 'b', 'r', 'g', 'b', 'r', 'g', 'b']  # red, green, blue
    markers = ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.']  # circle, triangle, square

    # Plot each array
    for arr, color, marker in zip(list_of_numeric_arrays, colors, markers):
        for point in arr:
            ax.scatter(point[0], point[1], point[2], c=color, marker=marker)

    # Labeling axes
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    plt.show()
    plt.pause(1)
    return


# def get_dead_spaces(rp, rs, data): # This will and does not work. Varian does not store the dead spaces. If you export and re-import there will be no dead space.
#     RelativePositions = []
#     DwellAbsPositions = []

#     for ChannelSequence in rp.ApplicationSetupSequence[0].ChannelSequence:
#         if int(ChannelSequence.ReferencedROINumber in data.channels_rois):
#             RelativePositions.append(ChannelSequence.BrachyControlPointSequence[0].ControlPointRelativePosition)
#             DwellAbsPositions.append(ChannelSequence.BrachyControlPointSequence[0].ControlPoint3DPosition)
    
#     contours_first_points = [contour[0] for contour in data.channel_contours]
#     disp = np.array(DwellAbsPositions) - np.array(contours_first_points)
#     # data.dead_spaces = np.sqrt(np.einsum('ij,ij->i', disp, disp)) #this is not the dead space actually, this is just the dist from tip to center dwell. The dead space should be added to this. 

def load_varian_dicom_data(rp_file: str, rs_file: str) -> DicomData:
    data = DicomData()

    # Channel ROI Numbers
    try:
        # we use the Planning file to get the channel ROI numbers
        rp_dataset = pydicom.dcmread(rp_file)
        data.channels_rois = [
            roi.ReferencedROINumber for roi in rp_dataset.ApplicationSetupSequence[0].ChannelSequence]
        data.channels_labels = [
            roi.SourceApplicatorID for roi in rp_dataset.ApplicationSetupSequence[0].ChannelSequence]
        data.channel_numbers = [
            number.ChannelNumber for number in  rp_dataset.ApplicationSetupSequence[0].ChannelSequence
        ]
        # Note: the above 3 lists are all read in, in order of ascending channel number.
        # The order of the above 3 is all correct and corresponds correctly to each other.

        data.patient_name = rp_dataset.PatientName.family_name
        data.patient_id = rp_dataset.PatientID
        data.plan_label = rp_dataset.RTPlanLabel
    except Exception as error_message:
        log.error(f"Reading RP Dicom file failed! {rp_file}\n{error_message}")

    #additional info
    try:
        data.approval_status = rp_dataset.ApprovalStatus
    except Exception as error_message:
        log.error("did not find Approval Status")
    try:
        data.operator = rp_dataset.OperatorsName
    except Exception as error_message:
        log.error("did not find Operators Name")
    
    global method_found
    method_found = False # method_found is redefined as false here so if 2 dicom folders are loaded in a row, then this value is reset to False each time
    # Central Axis data
    try:
        # CHECK IF A CENTRAL AXIS NEEDLE IS LABELED/USED
        centralaxisrefROINumber = None
        center_index = None
        for i, label in enumerate(data.channels_labels):
            for mylabel in ["Central Axis", "centralaxis"]:
                if mylabel.lower() in label.lower():
                    centralaxisrefROINumber = data.channels_rois[i]
                    center_index = i
                    break
            if centralaxisrefROINumber: 
                log.debug(f"Found central axis at ROI {centralaxisrefROINumber}")
                method_found = True
                break
    except Exception as error_message:
        log.error(f"Error locating central axis: {error_message}")    

    # IF THERE'S A CENTRAL AXIS, ADD IT TO DATA AND REMOVE IT FROM THE LIST
    if centralaxisrefROINumber:
        data.central_channel_roi = data.channels_rois[center_index]
        data.channels_labels.pop(center_index)
        data.channels_rois.pop(center_index)
        data.channel_numbers.pop(center_index)

    # Contour Data
    try:
        # We use the RS file to get the Applicator's ROI and contour data
        # We also use it to get the channel ROI data if we have their ROIS
        rs_dataset = pydicom.dcmread(rs_file)
        load_structures(data, rs_dataset)

        # cylinder from contour
        try:
            if data.central_channel_roi:  # if a central axis channel was found
                load_central_axis_varian(data, rs_dataset)
            else:  # use a surface contour for the cylinder
                load_cylinder_contour(data, rs_dataset)
                method_found = True
        except Exception as error_message:
            log.error(f"Loading RS Dicom surface struct or no central axis identified! {rs_file}\n{error_message}")
        
        if(method_found):
            # channels info
            if data.channels_rois:
                load_channels_varian(data, rs_dataset)
        else:
            get_app().window.no_central_axis_or_cylinder_outline()
    except Exception as error_message:
        log.error(f"Loading RS Dicom file failed! {rs_file}\n{error_message}")

    # # Get Default Needle Offset Value
    # try:
    #     get_dead_spaces(rp_dataset, rs_dataset, data)
    # except:
    #     pass


    log.debug(f"{data.toString()}")
    return data


def load_nucletron_dicom_data(rp_file: str, rs_file: str) -> DicomData:
    data = DicomData()
    global method_found
    method_found = False # method_found is redefined as false here so if 2 dicom folders are loaded in a row, then this value is reset to False each time
    # oncentraflag = False
    # if rp_dataset.Manufacturer == "Nucletron":
        # oncentraflag = True
    # Channel ROI Numbers
    try:
        # we use the Planning file to get the channel ROI numbers
        rp_dataset = pydicom.dcmread(rp_file)
        try:
            # Try to access an attribute of rp_dataset[0x300f,0x1000][0] to test if it is stored as raw binary or not.
            rp_dataset[0x300f,0x1000][0].StructureSetROISequence
            # If no attribute error was raised above, then we don't have to convert from binary.
            channels_data = rp_dataset[0x300f,0x1000]
        except AttributeError:
            # the tag [0x300f,0x1000] is not in the Dicom standard, and is a private tag created by Oncentra. 
            # Sometimes the contents are stored in a raw binary format, so we have to read it in using explicit instructions.
            from pydicom.filebase import DicomBytesIO
            from pydicom.filereader import read_sequence
            raw = rp_dataset[0x300f,0x1000].value
            fp = DicomBytesIO(raw)
            fp.is_little_endian = True
            fp.is_implicit_VR = True  # most private data uses implicit VR
            encoding = rp_dataset.read_encoding  # ['latin_1']
            seq = read_sequence(fp, is_implicit_VR=True, is_little_endian=True, bytelength=len(raw), encoding=encoding)
            
            channels_data = seq

        data.channels_rois = [int(channel_label.ROINumber) for channel_label in channels_data[0].StructureSetROISequence] 

        data.channels_labels = [
            roi.SourceApplicatorID for roi in rp_dataset.ApplicationSetupSequence[0].ChannelSequence] #not needed?
        try:
            data.channel_numbers = [
                number.ChannelNumber for number in  rp_dataset.ApplicationSetupSequence[0].ChannelSequence
            ]
        except:
            print("Channel Numbers not loaded -- Nucletron")

        data.patient_name = rp_dataset.PatientName.family_name
        data.patient_id = rp_dataset.PatientID
        data.plan_label = rp_dataset.RTPlanLabel
    except Exception as error_message:
        log.error(f"Reading RP Dicom file failed! {rp_file}\n{error_message}")
    
    #additional info
    try:
        data.approval_status = rp_dataset.ApprovalStatus
    except Exception as error_message:
        log.error("did not find Approval Status")
    try:
        data.operator = rp_dataset.OperatorsName
    except Exception as error_message:
        log.error("did not find Operators Name")

    # Central Axis data
    try:
        # CHECK IF A CENTRAL AXIS NEEDLE IS LABELED/USED
        # centralaxisrefROINumber = None
        # center_index = None
        for i, label in enumerate(data.channels_labels):
            if channels_data[0].StructureSetROISequence[i].ROIName.lower() in ["central axis", "centralaxis"]:
                data.central_channel_roi = int(channels_data[0].StructureSetROISequence[i].ROINumber)
                center_index = i

            if data.central_channel_roi is not None: 
                log.debug(f"Found central axis at channel {data.central_channel_roi}")
                method_found=True
                break


    except Exception as error_message:
        log.error(f"Error locating central axis: {error_message}")    

    # IF THERE'S A CENTRAL AXIS, ADD IT TO DATA AND REMOVE IT FROM THE LIST
    # (It is added above.  The following removes it from list.)
    if data.central_channel_roi is not None:
        data.channels_labels.pop(center_index)
        data.channels_rois.pop(center_index)
        data.channel_numbers.pop(center_index)

    # Contour Data
    try:
        # We use the RS file to get the Applicator's ROI and contour data
        # We also use it to get the channel ROI data if we have their ROIS
        rs_dataset = pydicom.dcmread(rs_file) #not using, since elekta stores their channels in the rp file. or do they?
        # explore_rp_rs(rp_dataset, rs_dataset)
        load_structures(data, rs_dataset)

        # cylinder from contour
        try:
            if data.central_channel_roi is not None:  # if a central axis channel was found
                load_central_axis_nucletron(data, channels_data)
            else:  # use a surface contour for the cylinder
                load_cylinder_contour(data, rs_dataset)
                method_found=True
        except Exception as error_message:
            log.error(f"Loading RS Dicom surface struct or no central axis identified! {rs_file}\n{error_message}")
        
        # channels info
        if(method_found):
            if data.channels_rois:
                load_channels_nucletron(data, channels_data, center_index)
        else:
            get_app().window.no_central_axis_or_cylinder_outline()
    except Exception as error_message:
        log.error(f"Loading RS Dicom file failed! {rs_file}\n{error_message}")

    log.debug(f"{data.toString()}")
    return data


def read_dicom_folder(folder_path: str):
        """Used to import a folder, check it for relevant dicom files, and set up the app for the data"""
        files = [ p for p in Path(folder_path).glob('**/*.dcm') if p.is_file()]

        log.debug(f"Found {files} in {folder_path}")

        # look for planning file first
        rp_file = None
        for file in files:
            if is_rp_file(file):
                rp_file = file
                break

        if not rp_file:  # if none of the files within the folder are a rp file
            log.info(f"No rp file was found at {folder_path}")

        # looking for the structure file
        rs_file = None
        for file in files:
            if is_rs_file(file):
                rs_file = file
                break

        if not rs_file:
            log.info(f"No rs file was found in {folder_path}")

        # get data from files
        log.debug(f"Planning file is: {rp_file}")
        log.debug(f"Structure file is: {rs_file}")

        # Determine the TPS
        rp_dataset = pydicom.dcmread(rp_file)
        manufacturer = rp_dataset.Manufacturer
        if manufacturer == "Varian Medical Systems":
            data = load_varian_dicom_data(rp_file, rs_file)
        if manufacturer == "Nucletron":
            data = load_nucletron_dicom_data(rp_file, rs_file)
        else:
            pass

        return data
