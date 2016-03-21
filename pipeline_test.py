from stl_read import *
from  slicer import *

if __name__ == '__main__':
    mesh = mesh.Mesh.from_file("halfsphere.stl")
    mesh = remove_duplicates_from_mesh(mesh)
    slice_layers = slicer_from_mesh(mesh, slice_height_from=0, slice_height_to=100, slice_step=1)
    print("dtc")
