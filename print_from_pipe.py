import inspect
import json
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.config.config_factory import ConfigFactory
from slicer.Print_pipeline import print_mesh
from slicer.shapes.mp5totree import get_mc_params
import pymplicit
from stl import mesh
import numpy as np
from slicer.mock_cpp import to_json_mc_params, m2stl_mesh
# from slicer.shapes.mp5tostl import puppy_magic


def print_from_pipe():


    mp5_as_json = "".join(sys.stdin.readlines())

    mp5 = json.loads(mp5_as_json)

    if 'printerSettings' in mp5:
        ConfigFactory(dict_conf=mp5['printerSettings'])
    else:
        ConfigFactory()
    import slicer.config.config as config
    config.reset()

    stls = []

    for son_position in range(len(mp5["root"]["children"])):
        mc = get_mc_params(mp5, son_position)
        mc_params = to_json_mc_params(mc)
        mp5_string = json.dumps(mp5["root"]["children"][son_position])

        pymplicit.build_geometry(mp5_string, mc_params)
        verts = pymplicit.get_verts()
        faces = pymplicit.get_faces()
        pymplicit.finish_geometry()

        stl = m2stl_mesh(verts, faces)
        stls.append(stl.data)

    stl = mesh.Mesh(np.concatenate(stls))

    # stl = puppy_magic(mp5)
    # stl.save("mp5.stl")
    print_mesh(stl, "mp5")

if __name__ == '__main__':
    print_from_pipe()
