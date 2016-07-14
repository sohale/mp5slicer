import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from slicer.print_tree.layer import Layer
from slicer.gcode_writer.G_buffer import G_buffer
from slicer.commons.utils import *
import time
from slicer.mesh_processing.mesh_operations import mesh as MPmesh
from slicer.config.config_factory import config_factory
from slicer.mesh_processing.slice import *
import slicer.print_tree.support as support
from slicer.print_tree.raft_layer import *
global start_time
global print_settings
from slicer.post_process.simple_routing import Simple_router
from slicer.post_process.boundary_finishing_touch import Boundary_finish
from slicer.post_process.extrusion_calculation import Cal_extrusion
from slicer.post_process.Tree_post_processor import Tree_post_processor
from slicer.post_process.gcode_writer_new import Gcode_writer

# @profile
def get_layer_list(polygon_layers, BBox, support_polylines_list = []):

    import slicer.config.config as config

    layer_list = []



    for layer_index in range(len(polygon_layers)):
        if config.useSupport:
            layer = Layer(layer_list,polygon_layers,layer_index,BBox,support_polylines_list[layer_index])
        else:
            layer = Layer(layer_list,polygon_layers,layer_index,BBox)
        layer_list.append(layer)


    # process skins
    for layer in layer_list:
        layer.prepare_skins()

    for layer in layer_list:
        layer.process_skins()
        layer.process_infill()

    if config.raft == True:
        raft_base = layer_list[0].get_raft_base()

        raft_layer = Raft_layer(True,False, BBox, raft_base)
        layer_list.insert(0, raft_layer)
        raft_layer = Raft_layer(False,False, BBox, raft_base)
        layer_list.insert(0, raft_layer)
        raft_layer = Raft_layer(False, True, BBox, raft_base)
        layer_list.insert(0, raft_layer)
        layer_list.insert(0, raft_layer)
        # layer_list.insert(0, raft_layer)


    return layer_list

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



def get_stl_from_file(stl_file_name):
    from stl import mesh
    import slicer.config.config as config


    return mesh.Mesh.from_file(stl_file_name)


# @profile
def get_polygon_layers(stl_mesh):
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

        layers_as_polygons[layer_index] = pyclipper.scale_to_clipper(layers_as_polygons[layer_index])
        # polygon_layers[layer_index] = pyclipper.SimplifyPolygons(polygon_layers[layer_index])
        # polygon_layers[layer_index] = pyclipper.CleanPolygons(polygon_layers[layer_index])


    if config.useAdaptiveSlicing:
        return layers_as_polygons, BBox, adaptive_thickness
    else:
        return layers_as_polygons, BBox

def print_from_stl(stl_mesh):
    config_factory("config/config.json")
    import slicer.config.config as config
    config.reset()

    start_time = time.time()
    polygon_layers, BBox = get_polygon_layers(stl_mesh)

    # generate support polylines from mesh directly

    if config.useSupport:
        from stl import mesh
        this_mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)
        move_to_center(this_mesh)
        import datetime
        support_start_time = datetime.datetime.now()
        support_polylines_list = support.Support(this_mesh).get_support_polylines_list()
        print('time for support')
        print(datetime.datetime.now() - support_start_time)
    ############## end of support polylines generation and feed to get_layer_list####################

    if config.useSupport:
        layer_list = get_layer_list(polygon_layers, BBox, support_polylines_list=support_polylines_list)
    else:
        layer_list = get_layer_list(polygon_layers, BBox)

    print_tree = []
    for layer in layer_list:
        print_tree.append(layer.G_print())

    TPPT = Tree_post_processor(print_tree)
    router = Simple_router()
    TPPT.add_task(router)

    TPPT.run()


    g_buffer = G_buffer(True, "mp5.gcode")
    g_buffer.add_layer_list(print_tree)
    g_buffer.print_Gcode()

# @profile
def main():
    args = sys.argv
    args = args[1:]
    stl_file_name = args[0]
    conf_file_name = args[1]
    config_factory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    start_time = time.time()
    stl_mesh = get_stl_from_file(stl_file_name)
    polygon_layers, BBox = get_polygon_layers(stl_mesh)

    # generate support polylines from mesh directly

    if config.useSupport:
        from stl import mesh
        stl_mesh = mesh.Mesh.from_file(stl_file_name)
        this_mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)
        move_to_center(this_mesh)
        import datetime
        support_start_time = datetime.datetime.now()
        support_polylines_list = support.Support(this_mesh).get_support_polylines_list()
        print('time for support')
        print(datetime.datetime.now() - support_start_time)
    ############## end of support polylines generation and feed to get_layer_list####################

    if config.useSupport:
        layer_list = get_layer_list(polygon_layers, BBox, support_polylines_list=support_polylines_list)
    else:
        layer_list = get_layer_list(polygon_layers, BBox)

    print_tree = []
    for layer in layer_list:
        print_tree.append(layer.G_print())

    TPPT = Tree_post_processor(print_tree)
    router = Simple_router()
    boundary_finisher = Boundary_finish()
    cal_extrusion = Cal_extrusion()

    name, dot, type = stl_file_name.partition('.')
    write_gcode = Gcode_writer(True, gcode_filename=name + ".gcode")

    TPPT.add_task(router)
    TPPT.add_task(boundary_finisher)
    TPPT.add_task(cal_extrusion) # extrusion calculation at the end because other task will change line group
    TPPT.add_task(write_gcode)
    TPPT.run()
    print(name + ".gcode")
    print('gcode written')
    # name, dot, type = stl_file_name.partition('.')
    # g_buffer = G_buffer(True, gcode_filename=name + ".gcode")
    # g_buffer.add_layer_list(print_tree)
    # g_buffer.print_Gcode()






if __name__ == '__main__':
    main()
