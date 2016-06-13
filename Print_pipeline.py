import inspect, os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from slicer.layer import Layer
from slicer.G_buffer import G_buffer
from slicer.utils import *
import time
from slicer.mesh_operations import mesh as MPmesh
import sys, getopt
from slicer.config_factory import config_factory
from slicer.slice import *
import slicer.support as support
global start_time
global print_settings


def get_layer_list(polygon_layers, BBox, support_polylines_list = []):

    import slicer.config as config

    layer_list = []
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))

    for layer_index in range(len(polygon_layers)):
        if config.useSupport:
            layer = Layer(layer_list,polygon_layers,layer_index,BBox,support_polylines_list[layer_index])
        else:
            layer = Layer(layer_list,polygon_layers,layer_index,BBox)
        layer_list.append(layer)

    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))

    # process skins
    for layer in layer_list:
        layer.prepare_skins()

    for layer in layer_list:
        layer.process_skins()
        layer.process_infill()

    return layer_list

def move_to_center(mesh):
    import slicer.printer_config as printer_config
    bbox = mesh.bounding_box()
    platform_center = {}
    if printer_config.origin == "center":
        platform_center["x"] = 0
        platform_center["y"] = 0
    else:
        platform_center["x"] = printer_config.build_platformX/2
        platform_center["y"] = printer_config.build_platformY/2
    objet_center = {}
    objet_center["x"] = (bbox.xmax - bbox.xmin)/2
    objet_center["y"] = (bbox.ymax - bbox.ymin)/2
    objet_center["x"] += bbox.xmin
    objet_center["y"] += bbox.ymin
    x_slide = platform_center["x"] - objet_center["x"]
    y_slide = platform_center["y"] - objet_center["y"]
    mesh.translate([x_slide,y_slide,0])







def get_polygon_layers(stl_file_name):
    from stl import mesh
    import slicer.config as config


    stl_mesh = mesh.Mesh.from_file(stl_file_name)
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
    this_mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))

    move_to_center(this_mesh)

    # this_mesh.translate([90,130,0])
    BBox = this_mesh.bounding_box()

    if config.useAdaptiveSlicing:
        adaptive_height_list, adaptive_thickness = adaptive_slicing(this_mesh, config.layerThickness, curvature_tol=0.6, cusp_height_tol=0.15, layer_thickness_choices=[0.2, 0.15, 0.1], does_visualize = False)
        slice_layers = slicer_from_mesh_as_dict(this_mesh, slice_height_from=BBox.zmin, slice_height_to=BBox.zmax, slice_step= config.layerThickness, sliceplanes_height=adaptive_height_list)
    else:
        slice_layers = slicer_from_mesh_as_dict(this_mesh, slice_height_from=BBox.zmin, slice_height_to=BBox.zmax, slice_step= config.layerThickness)

    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
    layers_as_polygons = polygonize_layers_from_trimed_dict(slice_layers)
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))

    for layer_index in range(len(layers_as_polygons)):

        layers_as_polygons[layer_index] = pyclipper.scale_to_clipper(layers_as_polygons[layer_index])
        # polygon_layers[layer_index] = pyclipper.SimplifyPolygons(polygon_layers[layer_index])
        # polygon_layers[layer_index] = pyclipper.CleanPolygons(polygon_layers[layer_index])


    if config.useAdaptiveSlicing:
        return layers_as_polygons, BBox, adaptive_thickness
    else:
        return layers_as_polygons, BBox




if __name__ == '__main__':
    import pyclipper
    args = sys.argv
    args = args[1:]
    stl_file_name = args[0]
    conf_file_name = args[1]
    config_factory(conf_file_name)


    start_time = time.time()
    polygon_layers, BBox  = get_polygon_layers(stl_file_name)
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))

    # generate support polylines from mesh directly

    if config.useSupport:
        from stl import mesh
        stl_mesh = mesh.Mesh.from_file(stl_file_name)
        this_mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)
        move_to_center(this_mesh)
        support_polylines_list = support.Support(this_mesh).get_support_polylines_list()
    ############## end of support polylines generation and feed to get_layer_list####################

    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
    if config.useSupport:
        layer_list = get_layer_list(polygon_layers,BBox, support_polylines_list = support_polylines_list)
    else:
        layer_list = get_layer_list(polygon_layers,BBox)
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
    name,dot,type = stl_file_name.partition('.')
    g_buffer = G_buffer(True, gcode_filename=name + ".gcode")
    for layer in layer_list:
        g_buffer.add_layer(layer.G_print())
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
    g_buffer.print_Gcode()
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))