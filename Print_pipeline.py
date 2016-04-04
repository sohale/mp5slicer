from Layer import Layer
from G_buffer import G_buffer
from pipeline_test import *


def get_layer_list(polygon_layers):
    layer_list = []
    for layer_as_polygons in polygon_layers:
        layer = Layer()
        layer_list.append(layer)
        layer.add_island(layer_as_polygons)
        # for poly in layer_as_polygons:
        #     layer.add_island(poly)



    return layer_list

def get_polygon_layers():
    from stl import mesh
    stl_mesh = mesh.Mesh.from_file("elephant.stl")
    # assume the center of the mesh are at (0,0)
    # translate x by 70
    stl_mesh.vectors[:,:,0]+=70
    # translate y by 70
    stl_mesh.vectors[:,:,1]+=70
    stl_mesh = remove_duplicates_from_mesh(stl_mesh)
    slice_layers = slicer_from_mesh(stl_mesh, slice_height_from=0, slice_height_to=100, slice_step=0.2)
    layers_as_polygons = polygonize_layers(slice_layers)
    layers_as_polygons = reord_layers(layers_as_polygons)

    return layers_as_polygons



if __name__ == '__main__':
    g_buffer = G_buffer()
    polygon_layers = get_polygon_layers()
    layer_list = get_layer_list(polygon_layers)
    for layer in layer_list:
        g_buffer.add_layer(layer.G_print())
    g_buffer.print_Gcode()