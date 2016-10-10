from slicer.mesh_processing.slice_mesh import slice_mesh
from slicer.print_tree.generate_print_tree import generate_tree
from slicer.post_process.refine_print_tree import refine_print_tree
import slicer.config.config as config

def print_mesh(mesh, stl_name):
    polygon_layers, our_mesh, BBox = slice_mesh(mesh)
    print_tree = generate_tree(polygon_layers, BBox)
    refine_print_tree(print_tree, stl_name)

#todo
def print_implicit():
    pass