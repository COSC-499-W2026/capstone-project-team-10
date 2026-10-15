import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.GeomAbs import GeomAbs_Plane
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods, TopoDS_Solid, TopoDS_Shape
from OCC.Core.gp import gp_Dir, gp_Ax2, gp_Pnt, gp_Vec
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.ShapeFactory import translate_shp
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeTorus

from classes.dicom.data import DicomData
from classes.logger import log
from classes.mesh.helper import face_is_plane, geom_plane_from_face
from classes.mesh.notch import CylinderNotch, NotchSettings

from classes.app import get_app


class BrachyCylinder:
    
    # returns the current config value of the cylinder (not currently in use.)
    @staticmethod
    def default_length() -> float: return get_app().values.config_values.get("CONFIG_CYLINDER_LENGTH")

    def shape(self) -> TopoDS_Shape:
        if self._shape:
            return self._shape

        # cylinder references
        cylinder_axis = gp_Dir(0, 0, 1)
        cylinder_vector = gp_Ax2(gp_Pnt(0, 0, 0), cylinder_axis)
        cylinder = BRepPrimAPI_MakeCylinder(cylinder_vector, self.diameter / 2, self.length)

        # Our goal is to find the highest Z face and remove it
        z_max = -300.0

        # We have to work our way through all the faces to find the highest Z face so we can remove it for the shell
        face_explorer = TopExp_Explorer(cylinder.Shape(), TopAbs_FACE)
        while face_explorer.More():
            face = topods.Face(face_explorer.Current())
            if face_is_plane(face):
                a_plane = geom_plane_from_face(face)

                # We want the highest Z face, so compare this to the previous faces
                a_pnt_loc = a_plane.Location()
                z = a_pnt_loc.Z()
                if z > z_max:
                    z_max = z
                    top_face = face
            face_explorer.Next()

        # applying fillet to whole cylinder
        fillet = BRepFilletAPI_MakeFillet(cylinder.Shape())
        for e in TopologyExplorer(top_face).edges():
            fillet.Add(self.diameter / 2, e)
        fillet.Build()
        cylinder = fillet.Shape()

        base_height = float(get_app().values.config_values.get("CONFIG_BASE_HEIGHT", 0.0))
        base_thickness = float(get_app().values.config_values.get("CONFIG_BASE_THICKNESS", 0.0))

        z_notch_offset = 0.0
        if self.expand_base and base_height > 0 and base_thickness > 0:
            cylinder = add_base(
                shape=cylinder,
                radius1=self.diameter / 2,
                base_thickness=base_thickness,
                base_height=base_height
            )
            # notch should sit on top of the collar
            z_notch_offset = base_height
        notch_diameter = self.diameter + (2.0 * base_thickness) if self.expand_base and base_height > 0 and base_thickness > 0 else self.diameter
        notch_length = min(10, base_height) if self.expand_base and base_height > 0 and base_thickness > 0 else 10
        self.notch = CylinderNotch(notch_diameter, NotchSettings(), notch_length)
        cylinder = add_notch(cylinder, self.notch, z_offset=z_notch_offset)

        return cylinder


    def setDiameter(self, diameter: float) -> None:
        self.diameter = diameter
        self._shape = None
        self._shape = self.shape()

    def setLength(self, length: float) -> None:
        self.length = length
        self._shape = None
        self._shape = self.shape()

    def enableBase(self, isBaseEnabled: bool) -> None:
        self.expand_base = isBaseEnabled
        self._shape = None
        self._shape = self.shape()

    def __init__(self, diameter: float = get_app().values.config_values.get("CONFIG_CYLINDER_DIAMETER"), expand_base: bool = False): 
        self.length = get_app().values.config_values.get("CONFIG_CYLINDER_LENGTH")
        self.diameter = diameter
        self.expand_base = expand_base
        self._shape = None
        self.notch = CylinderNotch(diameter, NotchSettings(), NotchSettings().height)


def get_brachy_cylinder(data: DicomData) -> BrachyCylinder:
    # if cylinder contour is provided in dicom file, then read diameter from it
    try: 
        point1 = np.asarray(data.cylinder_contour[0])
        point2 = np.asarray(data.cylinder_contour[-1])
        difference = point2 - point1
        diameter = np.sqrt((difference[0]) ** 2 +
                        (difference[1]) ** 2 + (difference[2]) ** 2)
        diameter = round(diameter, 1)

        log.debug(f"Cylinder results: \n Diameter: {diameter}")
    # if cylinder contour is not provided, then set to default value
    except Exception as error_message: 
        diameter = get_app().values.config_values.get("CONFIG_CYLINDER_DIAMETER")
        log.debug(f"No Cylinder surface contour, or error reading:\nDiameter set to default:"+str(diameter))

    return BrachyCylinder(diameter=diameter)

def add_base(shape: TopoDS_Solid, radius1: float, base_thickness: float, base_height: float):
    base_thickness = float(base_thickness)
    base_height = float(base_height)
    
    if base_height <= 0 or base_thickness <= 0:
        return shape  # consistent safe-guard

    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))

    outer_radius = radius1 + base_thickness

    outer = BRepPrimAPI_MakeCylinder(axis, outer_radius, base_height).Shape()
    inner = BRepPrimAPI_MakeCylinder(axis, radius1, base_height).Shape()

    collar = BRepAlgoAPI_Cut(outer, inner).Shape()
    return BRepAlgoAPI_Fuse(shape, collar).Shape()

def add_notch(shape: TopoDS_Shape, notch: CylinderNotch, z_offset: float = 0.0):
    if not notch:
        return shape

    notch_shape = notch.shape()
    # if z_offset and z_offset != 0.0:
    #     notch_shape = translate_shp(notch_shape, gp_Vec(0.0, 0.0, float(z_offset)))

    return BRepAlgoAPI_Fuse(shape, notch_shape).Shape()