from slicer.post_process.Tree_post_processor import Tree_post_processor
from slicer.post_process.simple_routing import Simple_router
from slicer.post_process.boundary_finishing_touch import Boundary_finish
from slicer.post_process.gcode_writer_new import GcodeGenerator

def refine_print_tree(print_tree, stl_file_name):
    simple_print_tree = []
    for layer in print_tree:
        simple_print_tree.append(layer.G_print())

    tree_post_processor = Tree_post_processor(simple_print_tree)
    router = Simple_router()
    boundary_finisher = Boundary_finish()
    # cal_extrusion = Cal_extrusion()


    name = stl_file_name.partition('.')[0]
    write_gcode = GcodeGenerator(gcode_filename=name + ".gcode")
    tree_post_processor.add_task(router)
    tree_post_processor.add_task(boundary_finisher)
    tree_post_processor.add_task(write_gcode)
    tree_post_processor.run()