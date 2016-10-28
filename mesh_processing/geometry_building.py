from mp5slicer.shapes.mp5totree import get_mc_params
import json
import numpy as np
import pymplicit
from stl import mesh


def build_geometry(mp5):
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

        return mesh.Mesh(np.concatenate(stls))


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
    mc_params = {"resolution": 200, "box": bb, "ignore_root_matrix": ignore_root_matrix}
    mc_params = json.dumps(mc_params)
    return mc_params