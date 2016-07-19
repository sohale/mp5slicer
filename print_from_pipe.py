import inspect
import os
import sys


sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from solidmodeler.clean_code.mp5tostl import puppy_magic
from slicer.Print_pipeline import print_mesh
from slicer.config.config_factory import config_factory
import json

def print_from_pipe():
    conf_file_name = sys.argv[1]
    config_factory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    mp5_as_json = sys.stdin.readlines()


    mp5 = json.load(mp5_as_json)

    stl = puppy_magic(mp5)
    stl.save("mp5.stl")
    print_mesh(stl, "mp5", False)


if __name__ == '__main__':
    print_from_pipe()