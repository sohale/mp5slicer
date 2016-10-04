import inspect
import json
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.config.config_factory import config_factory
from slicer.Print_pipeline import print_mesh
from slicer.shapes.mp5totree import get_mc_params
import pymplicit
import numpy as np
from stl import mesh


def print_from_pipe():
    conf_file_name = sys.argv[1]
    config_factory(conf_file_name)
    import slicer.config.config as config
    config.reset()

    mp5_as_json = "".join(sys.stdin.readlines())
    mp5 = '{"printerSettings":{"name":"test","layerThickness":0.2,"emptyLayer":0,"infillSpace":4,"topThickness":0.6,"paramSamples":75,"speedRate":1000,"circleSpeedRate":1000,"temperature":220,"inAirSpeed":7000,"flowRate":0.035,"criticalLength":35,"retractionSpeed":2400,"retractionLength":5,"shellNumber":3,"material":"PLA 2.85mm","autoZScar":true,"zScarGap":0.5,"critLayerTime":6,"filamentDiameter":2.85},"mp5-version":"0.3","root":{"type":"root","children":[{"type":"Difference","protected":false,"children":[{"type":"cylinder","displayColor":{"x":0.7675997200783986,"y":0.03892568708507049,"z":0.1754374135888661},"matrix":[46.276738560910324,0,0,0,0,71.03955320184234,0,0,0,0,10,0,0,0,0,1],"index":652818},{"type":"cylinder","displayColor":{"x":0.11421729990684737,"y":0.07562705374348999,"z":0.6324600862122098},"matrix":[43.70523314805503,0,0,-0.03336494987031813,0,23.811935098864172,0,-1.473401670043664,0,0,23.811935098864172,5.569059618774723,0,0,0,1],"index":2463576}],"initialSize":{"x":1,"y":1,"z":1},"displayColor":{"x":0.6745098039215687,"y":0.47843137254901963,"z":0.6509803921568628},"matrix":[0.7697738537889303,0,0,4.16759433777402,0,0.030894923516336208,-0.7691536190371745,1.3949227857422084,0,0.7691536190371742,0.030894923516336176,27.65249099731288,0,0,0,1],"index":1939910}]}}'

    stls = []
    mp5 = json.loads(mp5)

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

    combined_stl = mesh.Mesh(np.concatenate(stls))

    combined_stl.save("mp5.stl")
    print("done")
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
    mc_params = {"resolution": 200, "box": bb, "ignore_root_matrix": ignore_root_matrix}
    mc_params = json.dumps(mc_params)
    return mc_params



if __name__ == '__main__':
    print_from_pipe()
