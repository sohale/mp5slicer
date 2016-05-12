from Layer import Layer
from G_buffer import G_buffer
from utils import *
from clipper_operations import *
import time
from mesh_operations import mesh as MPmesh
import sys, getopt
from config_factory import config_factory

global start_time
global print_settings





def get_layer_list(polygon_layers,BBox):

    layer_list = []
    print("--- %s seconds ---" % (time.time() - start_time))
    for layer_index in range(len(polygon_layers)):

        layer = Layer(layer_list,polygon_layers,layer_index,BBox)
        layer_list.append(layer)

    print("--- %s seconds ---" % (time.time() - start_time))

    # process skins
    for layer in layer_list:
        layer.prepare_skins()

    for layer in layer_list:
        layer.process_skins()
        layer.process_infill()



    return layer_list


def get_polygon_layers(stl_file_name):
    from stl import mesh
    import config

    stl_mesh = mesh.Mesh.from_file(stl_file_name)
    print("--- %s seconds ---" % (time.time() - start_time))
    this_mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)
    print("--- %s seconds ---" % (time.time() - start_time))

    this_mesh.translate([90,130,0])
    BBox = this_mesh.bounding_box()



    slice_layers = slicer_from_mesh_as_dict(this_mesh, slice_height_from=BBox[4], slice_height_to=BBox[5], slice_step= config.layerThickness)
    print("--- %s seconds ---" % (time.time() - start_time))
    layers_as_polygons = polygonize_layers_from_trimed_dict(slice_layers)
    print("--- %s seconds ---" % (time.time() - start_time))

    for layer_index in range(len(layers_as_polygons)):
        layers_as_polygons[layer_index] = pyclipper.scale_to_clipper(layers_as_polygons[layer_index])
        # polygon_layers[layer_index] = pyclipper.SimplifyPolygons(polygon_layers[layer_index])
        # polygon_layers[layer_index] = pyclipper.CleanPolygons(polygon_layers[layer_index])


    return layers_as_polygons,BBox




if __name__ == '__main__':
    import pyclipper
    args = sys.argv
    args = args[1:]
    stl_file_name = args[0]
    conf_file_name = args[1]
    config_factory(conf_file_name)



    start_time = time.time()
    polygon_layers,BBox = get_polygon_layers(stl_file_name)
    print("--- %s seconds ---" % (time.time() - start_time))
    layer_list = get_layer_list(polygon_layers,BBox)
    print("--- %s seconds ---" % (time.time() - start_time))
    g_buffer = G_buffer()
    for layer in layer_list:
        g_buffer.add_layer(layer.G_print())
    print("--- %s seconds ---" % (time.time() - start_time))
    g_buffer.print_Gcode()
    print("--- %s seconds ---" % (time.time() - start_time))