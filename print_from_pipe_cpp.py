import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.Print_pipeline import print_mesh
from slicer.config.config_factory import config_factory
from slicer.shapes.mp5totree import get_mc_params
import json
import numpy as np
import pymplicit
from stl import mesh


def print_from_mp5():
    conf_file_name = sys.argv[1]
    config_factory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    stls = []
    mp5_as_json = "".join(sys.stdin.readlines())
    mp5 = json.loads(mp5_as_json)

    for son_position in range(len(mp5["root"]["children"])):
        mc = get_mc_params(mp5,son_position)
        mc_params = to_json_mc_params(mc)
        mp5_string = json.dumps(mp5["root"]["children"][son_position])


        pymplicit.build_geometry(mp5_string, mc_params)
        verts = pymplicit.get_verts()
        faces = pymplicit.get_faces()
        pymplicit.finish_geometry()

        stl = m2stl_mesh(verts, faces)
        stls.append(stl.data)

    combined_stl = mesh.Mesh(np.concatenate(stls))

    print_mesh(combined_stl, "mp5")


def m2stl_mesh(verts, faces):

    fv = verts[faces, :]

    data = np.zeros(fv.shape[0], dtype=mesh.Mesh.dtype)
    for i in range(fv.shape[0]):
        facet = fv[i]
        data['vectors'][i] = facet

    m = mesh.Mesh(data)
    return m

def to_json_mc_params(bbox):
    bb = {}
    bb["xmin"] = bbox.min.x.item(0)
    bb["xmax"] = bbox.max.x.item(0)

    bb["ymin"] = bbox.min.y.item(0)
    bb["ymax"] = bbox.max.y.item(0)

    bb["zmin"] = bbox.min.z.item(0)
    bb["zmax"] = bbox.max.z.item(0)
    ignore_root_matrix = False
    mc_params = {"resolution": 40, "box": bb, "ignore_root_matrix": ignore_root_matrix}
    mc_params = json.dumps(mc_params)
    return mc_params



if __name__ == '__main__':
    print_from_mp5()





