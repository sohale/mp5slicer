

import slicer.print_tree.support as support
import slicer.print_tree.support_new as support_new

from slicer.mesh_processing.slice_mesh import slice_mesh
from slicer.print_tree.generate_print_tree import generate_tree
from slicer.post_process.refine_print_tree import refine_print_tree
import slicer.config.config as config

def print_mesh(mesh, stl_name):
    polygon_layers, our_mesh, BBox = slice_mesh(mesh)

    if config.useSupport:
        # support_polylines_list = support.Support(our_mesh, BBox).get_support_polylines_list()
        support_polylines_list = support_new.generate_support(polygon_layers, BBox)
    else:
        support_polylines_list = []

    print_tree = generate_tree(polygon_layers, BBox, support_polylines_list)
    refine_print_tree(print_tree,stl_name)

#todo
def print_implicit():
    pass