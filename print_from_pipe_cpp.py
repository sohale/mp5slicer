import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from mp5slicer.legacy.Print_pipeline import print_mesh
from mp5slicer.config.config_factory import run_ConfigFactory_on_MP5_file
import json
from mp5slicer.mesh_processing.geometry_building import build_geometry


def print_from_mp5():

    mp5_as_json = "".join(sys.stdin.readlines())
    mp5 = json.loads(mp5_as_json)

    run_ConfigFactory_on_MP5_file(mp5, False)
    import mp5slicer.config.config as config
    config.reset()

    combined_mesh = build_geometry(mp5)
    print_mesh(combined_mesh, "mp5")

if __name__ == '__main__':
    print_from_mp5()
