

import slicer.print_tree.support as support
from slicer.mesh_processing.slice_mesh import slice_mesh
from slicer.print_tree.generate_print_tree import generate_tree
from slicer.post_process.refine_print_tree import refine_print_tree
import slicer.config.config as config

def print_mesh(mesh, stl_name):
    polygon_layers, BBox = slice_mesh(mesh)

    if config.useSupport:
        support_polylines_list = support.Support(mesh).get_support_polylines_list()
    else:
        support_polylines_list = []

    print_tree = generate_tree(polygon_layers, BBox, support_polylines_list)
    refine_print_tree(print_tree,stl_name)

#todo
def print_implicit():
    pass