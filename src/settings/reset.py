
from classes.app import get_app


def resetAllValues(values_dict: dict):
    """
    Resets all values in spin boxes to the values in the given dictionary and applies them to the views.
    """
    app = get_app()

    """
    Steps:
    1. read the value from the dictionary.
    2. set the spin box value.
    3. apply the value.
    """

    # Cylinder View values
    cylinder_diameter = values_dict.get("CONFIG_CYLINDER_DIAMETER")
    cylinder_length = values_dict.get("CONFIG_CYLINDER_LENGTH")
    cylinder_view = app.window.navigationmodel.views[1]
    cylinder_view.set_dimensions_mm(cylinder_diameter, cylinder_length)
    cylinder_view.base_thickness_field.set_millimetres(values_dict.get("CONFIG_BASE_THICKNESS"))
    cylinder_view.base_height_field.set_millimetres(values_dict.get("CONFIG_BASE_HEIGHT"))
    # if a DICOM file has already been imported, then apply the settings to update the views and models.
    if app.window.cylindermodel.cylinder is not None:
        app.window.navigationmodel.views[1].action_apply_settings() # apply the above settings

    # Channels View values
    channels_diameter = values_dict.get("CONFIG_CHANNELS_DIAMETER")
    needle_length = values_dict.get("CONFIG_DEADSPACE")
    threading_depth = values_dict.get("CONFIG_CHANNELS_THREADING_DEPTH")
    threading_radius = values_dict.get("CONFIG_CHANNELS_THREADING_DIAMETER")
    app.window.navigationmodel.views[2].ui.spinbox_diameter.setValue(channels_diameter)
    app.window.navigationmodel.views[2].ui.sb_needle_length.setValue(needle_length)
    app.window.navigationmodel.views[2].ui.sb_threading_dept.setValue(threading_depth)
    app.window.navigationmodel.views[2].ui.sb_threading_diameter.setValue(threading_radius)

    # do not need to check if is None (like for cylinder) because channelsmodel always has a diameter value, when initialized.
    app.window.navigationmodel.views[2].action_apply_settings() # apply the above settings
    # note for above: the needle lengths do not affect the view at all.  They are only used when
    # generating the .pdf reference sheet.

    """
    Tandem is more complicated than cylinder and channels.
    Cylinder and channels have their models reset from the action_apply_settings() methods.
    Cylinder and channels always exist.
    BUT tandem may:
        1. not exist yet.
        2. exist from being generated.
        3. exist from being imported.
    So always need to manually update tandem model values. Then:
        if (1), do not generate or import a tandem.
        if (2), action_set_tandem() to reset the view.
        if (3), do not generate a tandem, or need to do anything else.
    """

    # Tandem View values
    tandem_tip_height = values_dict.get("CONFIG_TANDEM_TIP_HEIGHT")
    tandem_channel_diameter = values_dict.get("CONFIG_TANDEM_CHANNEL_DIAMETER")
    tandem_stopper_diameter = values_dict.get("CONFIG_TANDEM_STOPPER_DIAMETER")
    tandem_tip_angle = values_dict.get("CONFIG_TANDEM_TIP_ANGLE")
    tandem_bend_radius = values_dict.get("CONFIG_TANDEM_BEND_RADIUS")
    tandem_rotation = values_dict.get("CONFIG_TANDEM_ROTATION")
    tandem_threading_depth = values_dict.get("CONFIG_TANDEM_THREADING_DEPTH")
    tandem_threading_diameter = values_dict.get("CONFIG_TANDEM_THREADING_DIAMETER")

    tandem_ui = app.window.navigationmodel.views[3].ui
    tandem_ui.sb_tandem_height.setValue(tandem_tip_height)
    tandem_ui.sp_channel_diameter.setValue(tandem_channel_diameter)
    tandem_ui.sp_stopper_diameter.setValue(tandem_stopper_diameter)
    tandem_ui.sp_bend_angle.setValue(tandem_tip_angle)
    tandem_ui.sb_bend_radius.setValue(tandem_bend_radius)
    tandem_ui.tandem_rotation.setValue(tandem_rotation)
    tandem_ui.tandem_rotation_2.setValue(tandem_rotation)

    # For tandem, must first reset the values in the model.
    tandemmodel = app.window.tandemmodel
    tandemmodel.tandem_length = tandem_tip_height
    tandemmodel.tandem_diameter = tandem_channel_diameter
    tandemmodel.stopper_diameter = tandem_stopper_diameter
    tandemmodel.tandem_angle = tandem_tip_angle
    tandemmodel.bend_radius = tandem_bend_radius
    tandemmodel.tip_angle = tandem_tip_angle
    tandemmodel.threading_depth = tandem_threading_depth
    tandemmodel.threading_diameter = tandem_threading_diameter

    # Now update the view, if applicable.
    # if there is a tandem already generated, update its values.  If not, don't generate one.
    # if tandem exists  
    if app.window.tandemmodel.exists(): 
        # if tandem is generated rather than imported
        if not app.window.tandemmodel.is_shape_imported:
            # apply the config settings
            app.window.navigationmodel.views[3].action_set_tandem()

    #Collet Preview Values
    export_ui = app.window.navigationmodel.views[4].ui

    needle_collet_od = values_dict.get("CONFIG_NEEDLE_COLLET_OUTER_DIAMETER")
    tandem_collet_od_outer = values_dict.get("CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER")
    tandem_collet_od_inner = values_dict.get("CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER")

    # Only set if keys exist (prevents None issues)
    if needle_collet_od is not None:
        export_ui.sb_needle_collet_od.setValue(needle_collet_od)
    if tandem_collet_od_outer is not None:
        export_ui.sb_tandem_collet_outer_od.setValue(tandem_collet_od_outer)
    if tandem_collet_od_inner is not None:
        export_ui.sb_tandem_collet_inner_od.setValue(tandem_collet_od_inner)
def getCurrentValues():
    """ 
    Collects all the currently set values and returns them as a dict.
    """
    # Collect the data to be stored in the config file.
    app = get_app()
    # 1. cylinder data
    default_cylinder_diameter = app.window.cylindermodel.cylinder.diameter
    default_length = app.window.cylindermodel.cylinder.length
    # the collar is read from the live settings, which Apply Settings writes
    base_thickness = app.values.config_values.get("CONFIG_BASE_THICKNESS")
    base_height = app.values.config_values.get("CONFIG_BASE_HEIGHT")
    notch = app.window.cylindermodel.cylinder.notch_settings
    # 2. channels data
    default_diameter = app.window.channelsmodel.diameter
    threading_depth = app.window.channelsmodel.threading_depth
    threading_diamenter = app.window.channelsmodel.threading_diamenter
    # 3. tandem data
    tandemmodel = app.window.tandemmodel
    tandem_channel_diameter_default = tandemmodel.tandem_diameter
    tandem_stopper_diameter_default = tandemmodel.stopper_diameter
    tandem_tip_angle_default = tandemmodel.tip_angle
    tandem_bend_radius = tandemmodel.bend_radius
    tandem_length = tandemmodel.tandem_length # this appears to coincide with Tandem Height in the GUI
    tandem_rotation = tandemmodel.rotation
    tandem_threading_depth = tandemmodel.threading_depth
    tandem_threading_diameter = tandemmodel.threading_diameter

    # 4. needle data - pulls the current value in the spin box
    default_needle_length = app.window.navigationmodel.views[2].ui.sb_needle_length.value() 

    # 5. collet data - pulls the current values in the spin boxes
    export_ui = app.window.navigationmodel.views[4].ui
    needle_collet_outer_diameter = export_ui.sb_needle_collet_od.value()
    collet_outer_diameter_outer = export_ui.sb_tandem_collet_outer_od.value()
    collet_outer_diameter_inner = export_ui.sb_tandem_collet_inner_od.value()

    # Create a dictionary containing the data.
    current_values = {
        "CONFIG_CYLINDER_DIAMETER": default_cylinder_diameter,
        "CONFIG_CYLINDER_LENGTH": default_length,
        "CONFIG_BASE_THICKNESS": base_thickness,
        "CONFIG_BASE_HEIGHT": base_height,
        "CONFIG_NOTCH_ENABLED": int(notch.enabled),
        "CONFIG_NOTCH_ANGLE": notch.angle,
        "CONFIG_NOTCH_WIDTH": notch.width,
        "CONFIG_NOTCH_DEPTH": notch.depth,
        "CONFIG_NOTCH_HEIGHT": notch.height,
        "CONFIG_CHANNELS_DIAMETER": default_diameter,
        "CONFIG_DEADSPACE": default_needle_length,
        "CONFIG_TANDEM_TIP_HEIGHT": tandem_length, # tandem_length may not actually be Tandem_Tip_Height_Default
        "CONFIG_TANDEM_CHANNEL_DIAMETER": tandem_channel_diameter_default, 
        "CONFIG_TANDEM_STOPPER_DIAMETER": tandem_stopper_diameter_default,
        "CONFIG_TANDEM_TIP_ANGLE": tandem_tip_angle_default,
        "CONFIG_TANDEM_BEND_RADIUS": tandem_bend_radius,
        "CONFIG_CHANNELS_THREADING_DEPTH": threading_depth,
        "CONFIG_CHANNELS_THREADING_DIAMETER": threading_diamenter,
        "CONFIG_TANDEM_ROTATION": tandem_rotation,
        "CONFIG_TANDEM_THREADING_DEPTH": tandem_threading_depth,
        "CONFIG_TANDEM_THREADING_DIAMETER": tandem_threading_diameter,
        "CONFIG_NEEDLE_COLLET_OUTER_DIAMETER": needle_collet_outer_diameter,
        "CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER": collet_outer_diameter_inner,
        "CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER": collet_outer_diameter_outer
    }

    return current_values
