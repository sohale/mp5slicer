import sys

from slicer.Print_pipeline import *
from slicer.config.config_factory import config_factory

args = sys.argv
args = args[1:]
stl_file_name = args[0]
conf_file_name = args[1]
config_factory(conf_file_name)




polygon_layers,BBox = get_polygon_layers(stl_file_name)
layer_list = get_layer_list(polygon_layers,BBox)

print_to_file = False
g_buffer = G_buffer(print_to_file)
for layer in layer_list:
    g_buffer.add_layer(layer.G_print())
g_buffer.print_Gcode()