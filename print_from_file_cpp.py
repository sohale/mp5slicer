import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.Print_pipeline import print_mesh
from slicer.config.config_factory import config_factory
import json
import numpy as np
import pymplicit


def print_from_mp5():
    mp5_file_name = sys.argv[2]
    conf_file_name = sys.argv[1]
    config_factory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    mp5 = json.loads(open(mp5_file_name).read())
    mp5 = mp5["root"]["children"][0]
    # mp5 = '{"type":"iellipsoid","displayColor":{"x":0.005798184165187736,"y":0.7660847647199172,"z":0.02514520193564107},"matrix":[10,0,0,100,0,10,0,100,0,0,10,5,0,0,0,1],"index":3241862}'
    mc = ' {"resolution":28,"box":{"xmin":-0.5,"xmax":0.5,"ymin":-0.5,"ymax":0.5,"zmin":-0.5,"zmax":0.5},"ignore_root_matrix":true}'


    pymplicit.build_geometry(mp5, mc)
    verts = pymplicit.get_verts()
    faces = pymplicit.get_faces()

    stl = m2stl_mesh(verts, faces)
    stl.save("mp5.stl")
    print_mesh(stl, "mp5")


def m2stl_mesh(verts, faces):
    from stl import mesh
    fv = verts[faces, :]

    data = np.zeros(fv.shape[0], dtype=mesh.Mesh.dtype)
    for i in range(fv.shape[0]):
        facet = fv[i]
        data['vectors'][i] = facet

    m = mesh.Mesh(data)
    return m


if __name__ == '__main__':
    print_from_mp5()





