from slicer.post_process.Tree_post_processor import Tree_post_processor
from slicer.post_process.simple_routing import Simple_router
from slicer.post_process.boundary_finishing_touch import Boundary_finish
from slicer.post_process.extrusion_calculation import Cal_extrusion
from slicer.post_process.gcode_writer_new import Gcode_writer

def refine_print_tree(print_tree ,stl_file_name ):
    simple_print_tree = []
    for layer in print_tree:
        simple_print_tree.append(layer.G_print())

    TPPT = Tree_post_processor(simple_print_tree)
    router = Simple_router()
    boundary_finisher = Boundary_finish()
    cal_extrusion = Cal_extrusion()


    name, dot, type = stl_file_name.partition('.')
    write_gcode = Gcode_writer( gcode_filename=name + ".gcode")
    TPPT.add_task(router)
    TPPT.add_task(boundary_finisher)
    # TPPT.add_task(cal_extrusion) # extrusion calculation at the end because other task will change line group
    TPPT.run()
    
    TPPT = Tree_post_processor(simple_print_tree)
    TPPT.add_task(write_gcode)
    TPPT.run()