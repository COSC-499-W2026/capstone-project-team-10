from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path 
import subprocess

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from classes.pdf.canvas import FooterCanvas

from classes.dicom.data import DicomData
from classes.logger import log
from classes.mesh.channel import NeedleChannel
from classes.mesh.cylinder import BrachyCylinder, TipShape
from classes.mesh.tandem import Tandem
from classes.app import get_app

import matplotlib.lines as lines

# BASEMAP = "basemap.png"


def calculate_protrusion_lengths(needles: list, needle_length: float):
    # This needs to have the needles so that the last point of each needle is at z=0.
    def calculate_cumulative_lengths(needles):
        cumulative_lengths = []

        for needle in needles:
            cumulative_length = 0

            for i in range(1, len(needle)):
                x1, y1, z1 = map(float, needle[i - 1])
                x2, y2, z2 = map(float, needle[i])
                segment_length = ((x2 - x1)**2 + (y2 - y1)
                                  ** 2 + (z2 - z1)**2)**0.5
                cumulative_length += segment_length

            cumulative_lengths.append(cumulative_length)

        return cumulative_lengths
    
    cumulative_lengths = calculate_cumulative_lengths(needles)
    protrusion_lengths = [needle_length - length for length in cumulative_lengths]
    return protrusion_lengths


def index_before_negative_point(channel_list):
    last_index = len(channel_list) - 1
    for i, point in enumerate(channel_list):
        if point[2] < 0:
            return max(0, i - 1)
    return last_index


def extract_points_from_channels(channels: list):
    """
    Retreives the points from NeedleChannels

    Returns:
        [ [x, y, z], [x, y, z], ...]
    """
    channels_list = []
    for channel in channels:
        channel_list = channel.get_points()

        # Filter out points where the z value is less than 0.
        # filtered_channel_list = [point for point in channel_list if point[2] > 0]
        reshape_channel_list = [point for point in channel_list]
        
        # Error Checks: We ignore all points below zero (below the bottom of the cylinder)
        # Find the index of the element just before the first instance in channel_list where the third element of the tuple is less than 0
        # last_pos_index = index_before_negative_point(filtered_channel_list)

        # Append last point at x,y,0 because channel.get_points() doesn't include the point at the base for some reason.
        # final_point = channel_list[last_pos_index][:]
        # final_point[2] = 0.0
        # channel_list.append(final_point)
        channels_list.append(reshape_channel_list)

    return channels_list

def extract_points_from_channels2(channels: list):
    """
    Retrieves the points from NeedleChannels
    1. if the last point(s) are below 0 on the needle, then it interpolates what the needle value is at the z=0 plane,
    deletes all the points with z<0, and appends the z=0 point on the end, so that the needle is truncated at z=0.
    2. if the last point on the needle is above the z=0 plane, then it creates a new point directly below the last point,
    but this one has z=0 to be on the z=0 plane, and appends that point to the needle so that the needle extends to the plane.
    3. If the needle stops at exactly z=0, then it does not modify it at all.

    Returns:
        [ [x, y, z], [x, y, z], ...]
    """

    channels_down_to_z0 = []
    for channel in channels:
        channel_pts = [] # The needle points are always stored with heights relative to the original cylinder height, and this is never changed.
        for point in channel.points:
            height_adjusted_point = point.copy()
            height_adjusted_point[2] += channel._offset # Adjust the height of the point so it is accurate for the current cylinder height.
            channel_pts.append(height_adjusted_point)
        
        for i, pt in enumerate(channel_pts):
            if pt[2] == 0: # if this point is exactly at z=0 then it is what we're looking for.
                channels_down_to_z0.append(channel_pts.copy())
                break # do not modify the channel at all.
            elif i >= len(channel_pts)-1: 
                # if we have reached the last point in the needle and the z>0 still, then "drop" a point down to z=0 with the same x,y values
                temp_channel = channel_pts.copy()
                temp_channel.append([pt[0], pt[1], 0])
                channels_down_to_z0.append(temp_channel)
                break # go to the next needle
            else: # This means the bottom point is below 0, so find it and interpolate the z value when the needle passes through the z=0 plane
                next_pt = channel_pts[i+1]
                if (pt[2]>0 and next_pt[2]<0):
                    # calculate the position x and y should be between them
                    rize = pt[2]-next_pt[2]
                    xsol = pt[0]
                    ysol = pt[1]
                    #if the x or y value of the 2 points is not matching
                    if(pt[0]!=next_pt[0]):
                        runx = pt[0]-next_pt[0]
                        mx = rize/runx
                        bx = pt[2]-mx*pt[0]
                        xsol = -bx/mx
                    if(pt[1]!=next_pt[1]):
                        runy = pt[1]-next_pt[1]
                        my = rize/runy
                        by = pt[2]-my*pt[1]
                        ysol = -by/my
                    temp_channel = channel_pts[0:i+1].copy() # get all the points that are above 0
                    temp_channel.append([xsol, ysol, 0])
                    channels_down_to_z0.append(temp_channel)
                    break
    
    
    return channels_down_to_z0


def flat_top_points(radius: float, length: float, spacing: float, rim: np.ndarray) -> np.ndarray:
    """
    Points covering a flat tip at z = length: a grid spacing apart inside the radius, plus the rim
    ring so a needle leaving at the edge still meets a point.
    """
    coords = np.arange(-radius, radius + spacing / 2, spacing)
    xs, ys = np.meshgrid(coords, coords)
    inside = xs ** 2 + ys ** 2 <= radius ** 2
    grid = np.column_stack([xs[inside], ys[inside], np.full(np.count_nonzero(inside), length)])
    ring = np.column_stack([rim[:, 0], rim[:, 1], np.full(len(rim), length)])
    return np.vstack([grid, ring])


def get_all_interstitial_lengths(cylinder: BrachyCylinder, needles: list, spacing: float = 0.1) -> list[float]:
    """
    Example usage:
    needle_interstital_lengths = get_all_interstitial_lengths(needles, base, tip, radius, spacing, CylLen=160)
    Where needles is a list of lists of needle coordinates.
    """

    def generate_cylinder_points(cylinder: BrachyCylinder, spacing: float) -> list[np.array]:
        length = cylinder.length
        base = np.array([0, 0, 0])
        tip = np.array([0, 0, length])
        radius = cylinder.diameter / 2 

        # Step 1: Generate variables
        vec = np.array(tip-base)
        vec_normalized = vec / \
            np.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
        # a flat tip has wall all the way up, a dome starts one radius below the top
        len_straight = length if cylinder.tip is TipShape.FLAT else length-radius
        NumStepsStraight = int(np.ceil(len_straight / spacing))
        end_straight_section = base + vec_normalized * len_straight
        CenterLineStraight = np.linspace(
            base, end_straight_section, NumStepsStraight, endpoint=False)
        num_thetas = int(np.ceil(2*np.pi*radius/spacing))
        thetas = np.linspace(0, 2*np.pi, num_thetas, endpoint=False)

        # Step 2: Generate the Straight Part of the Cylinder
        CylinderRing = np.ones((num_thetas, 3))
        CylinderRing[:, 0] = CylinderRing[:, 0] * radius * np.sin(thetas)
        CylinderRing[:, 1] = CylinderRing[:, 1] * radius * np.cos(thetas)
        CylinderStraight = np.ones((NumStepsStraight, num_thetas, 3))
        CylinderStraight[:] = CylinderRing
        CylinderStraight[:, :, 2] = CylinderStraight[:, :, 2]*CenterLineStraight[:, 2, np.newaxis]

        if cylinder.tip is TipShape.FLAT:
            return np.vstack([np.reshape(CylinderStraight, (-1, 3)),
                              flat_top_points(radius, length, spacing, CylinderRing)])

        # Step 3: Generate the Dome
        num_phis = int(np.ceil(np.pi/2*radius/spacing))
        phis = np.linspace(0, np.pi/2, num_phis)
        dome_radii = np.cos(phis)*radius

        dome_pts = np.ones((num_phis, num_thetas, 3))
        dome_pts[:, :, 0] = dome_pts[:, :, 0] * \
            np.sin(thetas) * dome_radii[:, np.newaxis]
        dome_pts[:, :, 1] = dome_pts[:, :, 1] * \
            np.cos(thetas) * dome_radii[:, np.newaxis]
        dome_pts[:, :, 2] = dome_pts[:, :, 2] * \
            np.sin(phis)[:, np.newaxis] * radius + len_straight

        # Step 4: Generate the Straight Part Normals
        vec_ring = CylinderRing - base
        # give each of the z component normals a bit of positive slope.
        vec_ring[:, 2] = 0.5
        vec_ring = vec_ring / \
            np.sqrt(np.einsum("ij,ij->i", vec_ring, vec_ring)
                    )[:, np.newaxis]
        vecs = np.ones((NumStepsStraight, num_thetas, 3))
        vecs[:] = vec_ring

        # Step 5: Generate the Dome Normals
        dome_base = end_straight_section
        dome_vecs = dome_pts - dome_base
        dome_vecs_reshaped = np.reshape(
            dome_vecs, (num_phis*num_thetas, 3))
        dome_disps_reshaped_normalized = dome_vecs_reshaped / \
            np.sqrt(np.einsum("ij,ij->i", dome_vecs_reshaped,
                    dome_vecs_reshaped))[:, np.newaxis]
        dome_vecs = np.reshape(
            dome_disps_reshaped_normalized, (num_phis, num_thetas, 3))

        cylinder_points = np.append(CylinderStraight, dome_pts)
        cylinder_points = np.reshape(
            cylinder_points, (NumStepsStraight*num_thetas+num_phis*num_thetas, 3))

        # Fix 1: the way this is made ends up adding a bunch of points 
        # (an amount of num_thetas) and vecs right at the tip of the dome
        # in this fix here we remove them.
        cylinder_points = cylinder_points[0:-num_thetas + 1]

        return cylinder_points

    def get_surface_intersection(surface_cloud, line_points, tol_mm=0.25):
        # Convert the input lists to numpy arrays for efficient calculations
        surface_cloud = np.array(surface_cloud)
        line_points = np.array(line_points)

        # Check if the input arrays have the correct shapes
        if surface_cloud.shape[1] != 3 or line_points.shape[1] != 3:
            raise ValueError("Input arrays must have shape (n, 3)")

        # Calculate the direction vector of the line
        line_displacement = line_points[1] - line_points[0]
        line_displacement = line_displacement.astype(float)
        line_direction = line_displacement/np.linalg.norm(line_displacement)

        # Calculate the vector from one point on the line to each point in the point cloud
        # Filter the surface cloud to only points that are not above or below the line segment (ie: only points that are within the z values of the line segment) to speed up calculations and avoid issues with points that are above or below the line.
        z_values = surface_cloud[:, 2]
        z_min = np.min(line_points[:, 2])
        z_max = np.max(line_points[:, 2])
        mask = np.logical_and(z_values >= z_min, z_values <= z_max)
        surface_cloud = surface_cloud[mask]

        vector_to_points = surface_cloud - line_points[0]

        # Project the vectors onto the line direction

        projection_onto_line = np.einsum('ij,j->i', vector_to_points, line_direction) # np.dot(vector_to_points, line_direction)


        # Calculate the closest points on the line to each point in the cloud
        closest_points_on_line = line_points[0] + \
            projection_onto_line[:, np.newaxis] * line_direction

        # Check if the closest points are within the bounds of the line segment
        within_line_segment_bounds = np.logical_and(
            0 <= projection_onto_line, projection_onto_line <= np.linalg.norm(line_displacement))

        # Filter out points that are not within the line segment bounds
        closest_points_on_line = closest_points_on_line[within_line_segment_bounds]

        if len(closest_points_on_line) == 0:
            # If no points are within the line segment bounds, return None
            return None

        # Calculate the distance between each point in the cloud and its closest point on the line
        distances = np.linalg.norm(
            surface_cloud[within_line_segment_bounds] - closest_points_on_line, axis=1)

        if np.min(distances) > tol_mm:
            return None

        # Find the index of the point with the minimum distance
        min_distance_index = np.argmin(distances)

        # Return the point on the line and the corresponding point on the surface cloud
        return closest_points_on_line[min_distance_index], surface_cloud[within_line_segment_bounds][min_distance_index]

    def get_interstitial_length(cylinder_points, linepoints):
        # Example Usage
        # length = get_interstitial_length(cylinder_points, linepoints)

        # Get the result from get_surface_intersection
        result = get_surface_intersection(cylinder_points, linepoints)
        if result != None:
            # Calculate the interstitial length based on the intersection point of the line segment with the surface.
            exit_point = result[0]
            end_point = linepoints[1]
            disp = end_point - exit_point
            length = np.linalg.norm(disp)
        else:
            length = 0
        return length

    cylinder_cloud = generate_cylinder_points(cylinder=cylinder, spacing=spacing)
    needle_interstitial_lengths = []

    for needle in needles:
        needle = np.array(needle)
        first_line_segment = np.vstack([needle[1], needle[0]])
        length = get_interstitial_length(cylinder_cloud, first_line_segment)

        if length is not None:
            needle_interstitial_lengths.append(length)
        else:
            needle_interstitial_lengths.append("Error")

    return needle_interstitial_lengths


def get_last_xy_points(needles):
    last_xy_points = []

    for needle in needles:
        # Check if the needle list is not empty and has at least 2 coordinates
        if needle and len(needle[-1]) >= 2:
            # Take only the first two coordinates (x and y)
            last_point = needle[-1][:2]
            last_xy_points.append(last_point)

    return last_xy_points

def get_point_at_z0(needles):
    z0points = []
    for needle in needles:
        for i, pt in needle:
            if i >= len(needle)-1: 
                # if we have reached the last point in the needle and the z>0 still, then "drop" a point down to z=0 with the same x,y values
                z0points.append([pt[0], pt[1], 0])
                break # go to the next needle
            elif pt[2] == 0: # if this point is exactly at z=0 then it is what we're looking for.
                z0points.append([pt[0], pt[1], pt[2]])
            else: # This means the bottom point is below 0, so find it and interpolate the z value when the needle passes through the z=0 plane
                next_pt = needle[i+1]
                if (pt[2]>0 and next_pt[2]<0):
                    # calculate the position x and y should be between them
                    rize = pt[2]-next_pt[2]
                    xsol = pt[0]
                    ysol = pt[1]
                    #if the x or y value of the 2 points is not matching
                    if(pt[0]!=next_pt[0]):
                        runx = pt[0]-next_pt[0]
                        mx = rize/runx
                        bx = pt[2]-mx*pt[0]
                        xsol = -bx/mx
                    if(pt[1]!=next_pt[1]):
                        runy = pt[1]-next_pt[1]
                        my = rize/runy
                        by = pt[2]-my*pt[1]
                        ysol = -by/my
                    z0points.append([xsol, ysol, 0])
    return z0points


def process_lengths_and_create_data(is_lengths, protrusion_lengths, label_list, number_list):
    needle_data = []

    for idx, (length_mm, protrusion_length) in enumerate(zip(is_lengths, protrusion_lengths), start=0):
        # Convert lengths from mm to cm and round to one decimal place
        length_cm = round(length_mm / 10, 1)
        protrusion_length_cm = round(protrusion_length / 10, 1)

        # Create a tuple for needle_data with protrusion length in the third column
        needle_info = (
            f"{label_list[idx]}", f"{number_list[idx]}", f"{length_cm} cm", f"{protrusion_length_cm} cm", "")
        needle_data.append(needle_info)

    return needle_data


def save_points_diagram(points: list,
                        number_list: list, 
                        circle_radius: float, 
                        output_filepath: Path, 
                        has_tandem: bool=False, 
                        tandem_rotation: float=0.0,
                        is_tandem_imported: bool=False,
                        include_collet_preview: bool=False):
    app = get_app()
    config = app.values.config_values
    channel_diam = config.get("CONFIG_CHANNELS_DIAMETER")
    #tandem will show up at config tandem value even if it is imported
    tandem_diam = config.get("CONFIG_TANDEM_CHANNEL_DIAMETER")

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))

    # Plot the circle
    circle = plt.Circle((0, 0), circle_radius, color='black', fill=False, clip_on=False)
    ax.add_artist(circle)

    # include only needles that are within 5cm of the cylinder.
    # (this is left here in case we choose to use it in the future.  Currently, all needles
    # passed to this method are within the cylinder.)
    #gets max x, y value that is within 5cm of cylinders origin for determining plotting
    #area
    #limit refers to the 5cm distance around the perimater of the cylinder where needles are allowed
    limit = 50+circle_radius
    plots_limit = circle_radius+2
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    for (x, y, z) in points:
        if(x>max_x and x <limit):
            max_x=x
        if(y>max_y and y <limit):
            max_y=y
        if(x<min_x and x >-limit):
            min_x=x
        if(y<min_y and x >-limit):
            min_y=y
    
    maxx = max(abs(max_x), abs(min_x))
    maxy = max(abs(max_y), abs(min_y))

    # Set axis limits to fit points inside a square with a border
    ax.set_xlim(min(min_x, -plots_limit), max(max_x, plots_limit))
    ax.set_ylim(min(min_y, -plots_limit), max(max_y, plots_limit))
    #makes frame invisible
    ax.set_frame_on(False)

    # Plot each point as a circle with a number inside or to the right or left if it does not fit inside
    # if channel diameter >= circle_radius/12 there is ~enough room to write numbers inside of channels
    # There could be some distorting of the image if there needles are outside of the cylinder
    if(channel_diam >= circle_radius/12 and maxx<circle_radius and maxy<circle_radius):
        for i, (x, y, z) in enumerate(points):
            #checks to make sure that needles are within 5 cm of center
            if(((np.sqrt(x**2+y**2))/2)<limit):
                ax.add_artist(plt.Circle((x, -y), channel_diam/2, color='black', fill=False, clip_on=False))
                ax.text(x, -y, str(number_list[i]), color='black', ha='center', va='center')
    else:
        for i, (x, y, z) in enumerate(points):
            #checks to make sure that needles are within 5 cm of center
            if((np.sqrt(x**2+y**2)/2)<limit):
                ax.add_artist(plt.Circle((x, -y), channel_diam/2, color='black', fill=False, clip_on=False))
                #so that text will print outside of needle channel to the right if the channel is too thin
                if(x<0):
                    ax.text(x-(channel_diam/2), -y, str(number_list[i]), color='black', ha='right', va='center')
                else:
                    ax.text(x+(channel_diam/2), -y, str(number_list[i]), color='black', ha='left', va='center')

    if has_tandem:
        try:
            tandem_channel_number = get_app().window.channelsmodel.get_tandem_channel().channel_number
        except AttributeError: # no channel is set as tandem, so don't write a channel number on the basemap.
            tandem_channel_number = ""
        if(tandem_diam >= circle_radius/12 and maxx<circle_radius and maxy<circle_radius):
            ax.add_artist(plt.Circle((0.0, 0.0), tandem_diam/2, color='black', fill=False))
            ax.text(0.0, 0.0, f'{tandem_channel_number}T', color='black', ha='center', va='center')
        else:
            ax.add_artist(plt.Circle((0.0, 0.0), tandem_diam/2, color='black', fill=False))
            ax.text((channel_diam/2), 0.0, f'{tandem_channel_number}T', color='black', ha='left', va='center')

        # if the tandem was generated, then display a dotted line on the pdf.
        if not is_tandem_imported:
            # add dotted line to indicate tandem direction.
            angle = tandem_rotation
            # construct a line segment of a fixed length, with the angle of rotation of the tandem
            line_length = circle_radius / 2
            end_pt_x = line_length * np.cos(np.radians(angle))
            # must make y-value negative bc the view is from the bottom of the cylinder, with  y-axis pointing down.
            # ie: o ---> x
            #     |
            #     y
            end_pt_y = -1* line_length * np.sin(np.radians(angle)) 
            x_values = [0, end_pt_x]
            y_values = [0, end_pt_y]
            # Line goes from (0,0) to (end_pt_x, end_pt_y)
            ax.add_artist(lines.Line2D(x_values, y_values,color='grey', linestyle='--'))
    # Include collet preview rings if selected
    if include_collet_preview:
        config = get_app().values.config_values

        needle_od = config.get("CONFIG_NEEDLE_COLLET_OUTER_DIAMETER")
        tandem_od_inner = config.get("CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER")
        tandem_od_outer = config.get("CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER")

        centers = []
        radii = []

        # Needle collet ring around each needle channel circle
        if needle_od:
            r_needle = float(needle_od) / 2.0
            for (x, y, z) in points:
                # match your same filter used when drawing channels
                if (np.sqrt(x**2 + y**2) / 2) < limit:
                    centers.append((float(x), -float(y)))   # MUST match your plotting: (x, -y)
                    radii.append(r_needle)

        # Tandem rings: BOTH inner + outer (same center as tandem channel: origin)
        if has_tandem:
            if tandem_od_outer:
                centers.append((0.0, 0.0))
                radii.append(float(tandem_od_outer) / 2.0)
            if tandem_od_inner:
                centers.append((0.0, 0.0))
                radii.append(float(tandem_od_inner) / 2.0)

        def ring_intersects_any(i):
            x1, y1 = centers[i]
            r1 = radii[i]
            for j in range(len(centers)):
                if i == j:
                    continue
                x2, y2 = centers[j]
                r2 = radii[j]

                # ignore concentric rings at the same center (tandem inner vs outer)
                if abs(x1 - x2) < 1e-6 and abs(y1 - y2) < 1e-6:
                    continue

                dx = x1 - x2
                dy = y1 - y2
                if (dx*dx + dy*dy) < (r1 + r2) * (r1 + r2):
                    return True
            return False

        for i in range(len(centers)):
            col = "red" if ring_intersects_any(i) else "green"
            ax.add_artist(
                plt.Circle(
                    centers[i],
                    radii[i],
                    fill=False,
                    linestyle="--",
                    color=col,
                    linewidth=1.5,
                    clip_on=False,
                )
            )
    # -------------------------------------------------------------------------------


    # Add a filled grey rectangle at the top center of the big circle
    notch = app.window.cylindermodel.cylinder.notch
    tick_width = notch.width
    tick_height = notch.height
    tick_color = 'black'
    # add the notch
    rect = plt.Rectangle((-tick_width / 2, circle_radius-0.05), # location of bottom left corner
                          tick_width, tick_height, color=tick_color, fill=False)
    ax.add_artist(rect)

    # Remove axis markers and numbering
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # add the words "Anterior" and "Posterior".
    # Anterior is the -y-axis, Posterior is the +y-axis.
    # Position the words so that they are just outside the circle.
    ax.text(0, +circle_radius + (circle_radius / 10), 
        "Anterior", color='black', ha='center', va='center', 
        fontsize=14, weight='bold')  # Adjust fontsize and weight

    ax.text(0, -circle_radius - (circle_radius / 10), 
            "Posterior", color='black', ha='center', va='center', 
            fontsize=14, weight='bold')  # Adjust fontsize and weight
  

    # Set axis aspect ratio to be equal
    ax.set_aspect('equal', adjustable='box')
    # Automatically adjust margins to fit the text
    fig.tight_layout(pad=1.0)  # pad: Padding around the elements in figure units


    # Set the Basemap Filepath
    png_path = output_filepath.joinpath('basemap.png')
    # Save the plot as a PNG file
    fig = plt.figure(1, dpi =1000000, clip_on=False)
    # add a black border to the figure.
    fig.patch.set_linewidth(1)
    fig.patch.set_edgecolor('black')

    fig.savefig(png_path, format='png')
    plt.close()
    return png_path

def channels_inside_cylinder(channels: list[NeedleChannel], diameter: float):
    """
    Returns the channels which go through the bottom of the cylinder.
    """
    radius = diameter / 2
    needles = extract_points_from_channels2(channels)
    z0points = [needle[-1] for needle in needles]
    channels_inside = []
    # if the last point of the channel is within the cylinder radius,
    # then keep that channel.
    for idx, point in enumerate(z0points):
        if np.sqrt(point[0]**2 + point[1]**2) <= radius:
            channels_inside.append(channels[idx])

    return channels_inside

# Add Deadspace
def add_deadspace(needles: list, deadspace_mm: float) -> list:
    """
    Returns new needles with added deadspace from tip [0] to next point [1].
    """
    deadspace_mm = float(deadspace_mm)

    if deadspace_mm <= 0:  # If no deadspace is requested, return the original needles
        return [[p[:] for p in needle] for needle in needles]  # Return a copy of the original needles
     
    extended_interstitial_length = []

    for needle in needles:
        pts = [p[:] for p in needle]  # copies points for each needle in needles list

        if len(pts) < 2:
            extended_interstitial_length.append(pts)
            continue

        tip = np.array(pts[0], dtype=float)
        nxt = np.array(pts[1], dtype=float)

        d = tip - nxt
        n = np.linalg.norm(d)

        # If the needle has zero length or if no deadspace is requested, keep it as is.
        if n == 0:
            log.warning("Deadspace not applied: zero-length first segment for a needle") ## Temporary Log warning, will add an error message in Ui 
            get_app().window.channel_display_warning()
            extended_interstitial_length.append(pts)
            continue

        u = d / n
        new_tip = tip + u * deadspace_mm

        pts[0] = [float(new_tip[0]), float(new_tip[1]), float(new_tip[2])]
        extended_interstitial_length.append(pts)

    return extended_interstitial_length

#Minimum Deadspace Calculation
# def force_min_interstitial(interstitial_lengths: list, min_deadspace: float = 6.0) -> list:
#     """
#     If any intersitial length is below the surface of the cylinder use the cylinder surface cloud to calculate the necessary deadspace to add and use that instead. 
#     """
   
#######################################################
# pdf generation
#######################################################
def generate_pdf(
        dicom: DicomData, 
        cylinder: BrachyCylinder,
        channels: list[NeedleChannel],
        filepath: Path,
        needle_length: float,
        has_tandem: bool, 
        tandem_rotation: float, 
        is_tandem_imported: bool,
        include_collet_preview: bool=False):

    app = get_app()

    # Get today's date in the format "Month Day, Year"
    today_date = datetime.today().strftime('%B %d, %Y')

    # Header information
    header_info = "Patient Specific Cylindrical Template Reference Sheet"
    patient_name = dicom.patient_name
    patient_id = dicom.patient_id
    plan_label = dicom.plan_label or "N/A"

    # Create a PDF document
    pdf = SimpleDocTemplate(str(filepath), pagesize=letter)

    # Content elements for the PDF
    content = []

    # Add header information
    header_style = ParagraphStyle(
        'Header1',
        parent=getSampleStyleSheet()['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,  # Hardcoded font size in points
        alignment=1,  # 0=Left, 1=Center, 2=Right
    )

    header_text = "<u>{}</u>".format(header_info)
    content.append(Paragraph(header_text, header_style))

    # Center alignment for the following paragraphs
    centered_style = getSampleStyleSheet()['Normal']
    centered_style.alignment = 1  # 0=Left, 1=Center, 2=Right

    left_style = getSampleStyleSheet()['Normal']
    left_style.alignment = 0  # 0=Left, 1=Center, 2=Right

    content.append(Paragraph(f"Date: {today_date}", left_style))
    content.append(Paragraph(f"Patient Name: {patient_name}", left_style))
    content.append(Paragraph(f"Patient ID: {patient_id}", left_style))
    content.append(
        Paragraph(f"Plan Label: {plan_label} <br/> <br/>", left_style))
    content.append(Paragraph("<br/>", centered_style))

    # Add table with needle data
    # use only the channels that are inside the cylinder
    diameter = cylinder.diameter
    channels_inside = channels_inside_cylinder(channels, diameter)
    needles_inside = extract_points_from_channels2(channels_inside)

    """
    Use deadspace calculations to extend needles for interstitial length calculation.
    """
    # Read deadspace from config (defaults to 6mm)
    config = get_app().values.config_values
    deadspace_mm = float(config.get("CONFIG_DEADSPACE", 6.0))

    # Extend a copy of the needles for calculation only (do not change originals)
    needles_for_calc = add_deadspace(needles_inside, deadspace_mm)

    # Use the extended needles for interstitial length calculation
    interstitial_lengths = get_all_interstitial_lengths(
        cylinder=cylinder,
        needles=needles_for_calc
)

    protrusion_lengths = calculate_protrusion_lengths(needles_inside, needle_length)
    # TODO: Add needle label and channel number instead of "Needle 1" etc.
    #length_label = "Protruding Length for " + str(needle_length) + "mm needle"
    data = [["Name","Channel Number", "Extension\n(Interstitial Length)"]]

    label_list = [channel.label for channel in channels_inside]
    number_list = [channel.channel_number for channel in channels_inside]
    for label, channel_number, interstitial_length, protruding_length, blank \
    in process_lengths_and_create_data(interstitial_lengths, protrusion_lengths, label_list, number_list):
        data.append([label, channel_number, interstitial_length])

    if has_tandem:
        tandem_label = app.window.dicommodel.data.tandem_channel #there isn't anything here if tandem is manually added without a tandem channel imported?
        if tandem_label is None:
            tandem_label = "Tandem (no channel selected)"
        try:
            tandem_channel_number = app.window.channelsmodel.get_tandem_channel().channel_number #there isn't anything here if tandem is manually added without a tandem channel imported?
        except AttributeError: # no channel is set as tandem, so write "N/A" for tandem channel number
            tandem_channel_number = ""
        data.append([tandem_label, tandem_channel_number, ""])

    table = Table(data)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ADD8E6")), # 1st row
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), # 1st row
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # 1st row
        ('VALIGN', (0,0), (-1, 0), 'MIDDLE'), # 1st row
        ('GRID', (0,0), (-1,-1), 1, colors.black), # entire table
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), # entire table
        ('BACKGROUND', (0, 1), (-1, -1), colors.white) # the rows containing the data
    ])
    """
    TableStyle([]):
    - passing it a sequence of commands, each command is a tuple identified by its 
        first element which is a string; the remaining elements of the command tuple 
        represent the start and stop cell coordinates of the command and possibly 
        thickness and colors, etc.
    - see this link for more info on TableStyle:
    https://docs.reportlab.com/reportlab/userguide/ch7_tables/#tablesetstyletblstyle
    - for example: 
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke) = ('COMMAND', (column,row), (column,row), color)
    - note: (column, row) is inclusive, 0 indexed, and negative values indicate to start from the end
        (ex column = -1 means the farthest right column, row = -1 means the bottom row)
    - 
    """
    table.setStyle(table_style)
    content.append(table)

    # Add the image to the PDF
    # Adjust width and height as needed
    pdf_output_dir = filepath.parent
    circle_radius = cylinder.diameter / 2


    last_xy_points = [needle[-1] for needle in needles_inside]
    
    png_path = save_points_diagram(last_xy_points, number_list, circle_radius, pdf_output_dir, has_tandem=has_tandem,
                                    tandem_rotation=tandem_rotation, is_tandem_imported=is_tandem_imported, include_collet_preview=include_collet_preview)

    # build the image for pdf with specified width and height.
    # kind='proportional' means keep the aspect ratio, so the width/height become max values.
    img = Image(str(png_path), width=5.75*inch, height=10*inch, kind='proportional')
    #img._restrictSize(7.5*inch, 10*inch) # an alternate possible way to size the image

    content.append(Spacer(1, 0.25*inch))
    content.append(img)

    # Build and save the PDF document
    pdf.build(content, canvasmaker=FooterCanvas)

    # Open the generated PDF using the default PDF viewer
    try:
        import os
        if os.name == 'nt':  # Check if on Windows
            try:
                # try opening the pdf using os.startfile
                os.startfile(str(filepath))
            except:
                # if os.startfile throws and exception, then try opening the pdf with subprocess.Popen
                subprocess.Popen(['start', str(filepath)], shell=True)
        elif os.name == 'posix':  # Check if on macOS/Linux
            subprocess.Popen(['open', str(filepath)])
    except Exception as e:
        print(f"Unable to open the PDF: {e}")

    log.info('wait')