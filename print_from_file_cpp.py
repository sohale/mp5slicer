import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from mp5slicer.legacy.Print_pipeline import print_mesh
from mp5slicer.config.config_factory import ConfigFactory
import json
from mp5slicer.mesh_processing.geometry_building import build_geometry



def print_from_mp5():
    mp5_as_json = "".join(sys.stdin.readlines())

    mp5 = json.loads(mp5_as_json)

    config_select = {0:"mp5slicer/config/config.mp5",
                     1:"mp5slicer/config/config_0.mp5",
                     2:"mp5slicer/config/config_1.mp5"}

    dict_conf_file = config_select[mp5['printerSettings']['config_select']]

    with open(dict_conf_file) as data_file:
        dict_conf = json.load(data_file)
    # hack to force config to_file in print_from_file_cpp to true
    dict_conf['TO_FILE'] = True

    if 'printerSettings' in mp5:
        ConfigFactory(dict_conf=dict_conf)
    else:
        ConfigFactory()

    import mp5slicer.config.config as config
    config.reset()



    combined_mesh = build_geometry(mp5)
    print_mesh(combined_mesh, "mp5")




if __name__ == '__main__':
    print_from_mp5()