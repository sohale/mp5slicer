import inspect
import json
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from mp5slicer.shapes.mp5tostl import puppy_magic
from mp5slicer.legacy.Print_pipeline import print_mesh
from mp5slicer.config.config_factory import ConfigFactory



def print_from_mp5():

    mp5_file_name = sys.argv[2]
    conf_file_name = sys.argv[1]
    ConfigFactory(conf_file_name)
    import mp5slicer.config.config as config
    config.reset()


    mp5 = json.load(open(mp5_file_name))


    stl = puppy_magic(mp5)
    # iobj = json2implicit_func(json)
    # iobj.implicitGradient(x)
    # iobj.implicitFunction(x)
    # stl = demo_combination_plus_qem(iobj)
    stl.save("mp5.stl")
    print_mesh(stl, "mp5")
    # g = slice(stl, iobj)

if __name__ == '__main__':
    print_from_mp5()
