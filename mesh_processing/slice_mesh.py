from slicer.mesh_processing.mesh_operations import mesh as MPmesh
from slicer.mesh_processing.slice import adaptive_slicing, slicer_from_mesh_as_dict
from slicer.commons.utils import polygonize_layers_from_trimed_dict, scale_list_to_clipper
import pyclipper

def move_to_center(mesh):
    import slicer.config.printer_config as printer_config
    bbox = mesh.bounding_box()
    platform_center = {}
    if printer_config.origin == "center":
        platform_center["x"] = 0
        platform_center["y"] = 0
    else:
        platform_center["x"] = printer_config.build_platformX / 2
        platform_center["y"] = printer_config.build_platformY / 2
    objet_center = {}
    objet_center["x"] = (bbox.xmax - bbox.xmin)/2 
    objet_center["y"] = (bbox.ymax - bbox.ymin)/2
    objet_center["x"] += bbox.xmin
    objet_center["y"] += bbox.ymin
    x_slide = platform_center["x"] - objet_center["x"]
    y_slide = platform_center["y"] - objet_center["y"]
    mesh.translate([x_slide,y_slide,0])


def slice_mesh(stl_mesh):

    import slicer.config.config as config


    this_mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)

    move_to_center(this_mesh)

    # this_mesh.translate([90,130,0])
    BBox = this_mesh.bounding_box()

    if config.useAdaptiveSlicing:
        adaptive_height_list, adaptive_thickness = adaptive_slicing(this_mesh, config.layerThickness, curvature_tol=0.6, cusp_height_tol=0.15, layer_thickness_choices=[0.2, 0.15, 0.1], does_visualize = False)
        slice_layers = slicer_from_mesh_as_dict(this_mesh, slice_height_from=BBox.zmin, slice_height_to=BBox.zmax, slice_step= config.layerThickness, sliceplanes_height=adaptive_height_list)
    else:
        slice_layers = slicer_from_mesh_as_dict(this_mesh, slice_height_from=BBox.zmin, slice_height_to=BBox.zmax, slice_step= config.layerThickness)

    layers_as_polygons = polygonize_layers_from_trimed_dict(slice_layers)

    for layer_index in range(len(layers_as_polygons)):
        # scale test
        layers_as_polygons[layer_index] = scale_list_to_clipper(layers_as_polygons[layer_index])
        # layers_as_polygons[layer_index] = pyclipper.scale_to_clipper(layers_as_polygons[layer_index])

        # polygon_layers[layer_index] = pyclipper.SimplifyPolygons(polygon_layers[layer_index])
        # polygon_layers[layer_index] = pyclipper.CleanPolygons(polygon_layers[layer_index])

    # raise Tiger

    if config.useAdaptiveSlicing:
        return layers_as_polygons, this_mesh, BBox, adaptive_thickness
    else:
        return layers_as_polygons, this_mesh, BBox