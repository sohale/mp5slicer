import inspect
import json
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.config.config_factory import ConfigFactory
from slicer.Print_pipeline import print_mesh
from slicer.shapes.mp5tostl import puppy_magic


def print_from_pipe():
    conf_file_name = sys.argv[1]
    ConfigFactory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    mp5_as_json = "".join(sys.stdin.readlines())

    mp5 = json.loads(mp5_as_json)

    stl = puppy_magic(mp5)
    # stl.save("mp5.stl")
    print_mesh(stl, "mp5")

if __name__ == '__main__':
    print_from_pipe()
