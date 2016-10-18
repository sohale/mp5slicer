import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.Print_pipeline import print_mesh
from slicer.config.config_factory import ConfigFactory
from slicer.shapes.mp5totree import get_mc_params
import json
import numpy as np
import pymplicit
from stl import mesh
from slicer.mesh_processing.geometry_building import build_geometry


def print_from_mp5():

    mp5_as_json = "".join(sys.stdin.readlines())

    mp5 = json.loads(mp5_as_json)

    config_select = {0:"slicer/config/config_0.mp5",
                     1:"slicer/config/config_1.mp5",
                     2:"slicer/config/config_2.mp5"}

    dict_conf_file = config_select[mp5['printerSettings']['config_select']]

    with open(dict_conf_file) as data_file:    
        dict_conf = json.load(data_file)

    if 'printerSettings' in mp5: 
        ConfigFactory(dict_conf=dict_conf)
    else:
        ConfigFactory()
    import slicer.config.config as config
    config.reset()

    combined_mesh = build_geometry(mp5)
    print_mesh(combined_mesh, "mp5")



if __name__ == '__main__':
    print_from_mp5()
