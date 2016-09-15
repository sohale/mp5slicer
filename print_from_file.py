import inspect
import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from slicer.config.config_factory import ConfigFactory
from slicer.Print_pipeline import print_mesh

def print_from_file():
    args = sys.argv
    args = args[1:]
    stl_file_name = args[0]
    conf_file_name = args[1]
    ConfigFactory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    mesh = get_stl_from_file(stl_file_name)
    print_mesh(mesh, stl_file_name)


def get_stl_from_file(stl_file_name):
    from stl import mesh
    return mesh.Mesh.from_file(stl_file_name)

if __name__ == '__main__':
    print_from_file()