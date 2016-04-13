from Layer import Layer
from G_buffer import G_buffer
from pipeline_test import *
from Skins import *
import time
from mesh_operations import mesh as MPmesh

global start_time

def get_skins(polygon_layers):
    skins = intersect_all_layers(polygon_layers)
    return skins



def get_layer_list(polygon_layers,BBox):

    layer_list = []
    # skins = get_skins(shells)
    print("--- %s seconds ---" % (time.time() - start_time))
    for layer_index in range(len(polygon_layers)):
        layer = Layer(layer_list,polygon_layers,layer_index,BBox)
        layer_list.append(layer)
        # layer.add_island(polygon_layers[layer_index])
        # for poly in layer_as_polygons:
        #     layer.add_island(poly)
    print("--- %s seconds ---" % (time.time() - start_time))

    # process skins
    for layer in layer_list:
        layer.process_skins()
        layer.process_infill()



    return layer_list

def bounding_box(stl_mesh):
    import numpy as np
    return np.array([np.min(stl_mesh.x),
                        np.max(stl_mesh.x),
                        np.min(stl_mesh.y),
                        np.max(stl_mesh.y),
                        np.min(stl_mesh.z),
                        np.max(stl_mesh.z)
                        ])

def get_polygon_layers():
    from stl import mesh
    stl_mesh = mesh.Mesh.from_file("cyl_cyl.stl")
    print("--- %s seconds ---" % (time.time() - start_time))
    mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)
    print("--- %s seconds ---" % (time.time() - start_time))
    # assume the center of the mesh are at (0,0)
    # translate x by 70
    mesh.triangles[:,:,0]+= 70
    # translate y by 70
    mesh.triangles[:,:,1]+= 70
    print("--- %s seconds ---" % (time.time() - start_time))
    BBox = bounding_box(stl_mesh)
    cut = BBox[4:].tolist()
    BBox = [0,150,0,150] + cut

    slice_layers = slicer_from_mesh_as_dict(mesh, slice_height_from=BBox[4], slice_height_to=BBox[5], slice_step=0.3)
    print("--- %s seconds ---" % (time.time() - start_time))
    layers_as_polygons = polygonize_layers_from_trimed_dict(slice_layers)
    print("--- %s seconds ---" % (time.time() - start_time))
    # for layer in layers_as_polygons:
    #     vizz_2d_multi(layer)
    # layers_as_polygons = reord_layers(layers_as_polygons)

    return layers_as_polygons,BBox

# def decimal_to_float(arr):
#     for layer in arr



if __name__ == '__main__':
    import pyclipper


    start_time = time.time()
    g_buffer = G_buffer()
    polygon_layers,BBox = get_polygon_layers()
    for layer in polygon_layers:
        pyclipper.scale_to_clipper(layer)
        pyclipper.SimplifyPolygons(layer)
        pyclipper.CleanPolygons(layer)
    print("--- %s seconds ---" % (time.time() - start_time))
    pyclipper.scale_to_clipper(polygon_layers)
    layer_list = get_layer_list(polygon_layers,BBox)
    for layer in layer_list:
        g_buffer.add_layer(layer.G_print())
    g_buffer.print_Gcode()