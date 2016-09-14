from slicer.post_process.Tree_post_processor import TreePostProcessor
from slicer.post_process.simple_routing import SimpleRouter
from slicer.post_process.boundary_finishing_touch import BoundaryFinish
from slicer.post_process.gcode_writer_new import GcodeGenerator


def refine_print_tree(print_tree, stl_file_name):
    simple_print_tree = []
    for layer in print_tree:
        simple_print_tree.append(layer.G_print())

    tree_post_processor = TreePostProcessor(simple_print_tree)
    router = SimpleRouter()
    boundary_finisher = BoundaryFinish()
    # cal_extrusion = Cal_extrusion()

    name = stl_file_name.partition('.')[0]
    write_gcode = GcodeGenerator(gcode_filename=name + ".gcode")
    tree_post_processor.add_task(router)
    tree_post_processor.add_task(boundary_finisher)
    tree_post_processor.add_task(write_gcode)
    tree_post_processor.run()
