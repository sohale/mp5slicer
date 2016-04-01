from stl_read import *
from  slicer import *
import pyclipper
from raytracer import *

def polygonize_layers(slice_layers):
    newslices = []
    for layer in slice_layers:
        newlayer = []
        for line in layer:
            line[0].pop()
            line[1].pop()
            newlayer.append(line)
        newslices.append(newlayer)

    slicesAsPolygons = []
    for slicee in newslices:
        polygons = []
        slicesAsPolygons.append(polygons)

        while True:
            try:
                line = slicee.pop()
            except IndexError:
                break

            start = line[0]
            end = line[1]

            newPolygon = []
            polygons.append(newPolygon)

            newPolygon.append(start)
            newPolygon.append(end)
            continuePolygon = True
            # Is there a new line i the polygon
            while continuePolygon:
                continuePolygon = False
                pointNotFound = True
                slicee2 = list(slicee)
                while pointNotFound:
                    try:
                        line2 = slicee2.pop()
                    except IndexError:
                        break
                    linePoint1 = line2[0]
                    linePoint2 = line2[1]
                    if (np.fabs(end[0] - linePoint2[0]) < 0.00001) and (np.fabs(end[1] - linePoint2[1]) < 0.00001):
                        if start != linePoint1:
                            # An other line in the polygon was found
                            slicee.remove(line2)
                            start = linePoint2
                            end = linePoint1
                            newPolygon.append(end)
                            continuePolygon = True
                            pointNotFound = False
                    if (np.fabs(end[0] - linePoint1[0]) < 0.00001) and (np.fabs(end[1] - linePoint1[1]) < 0.00001):
                        if start != linePoint2:
                            slicee.remove(line2)
                            start = linePoint1
                            end = linePoint2
                            newPolygon.append(end)
                            continuePolygon = True
                            pointNotFound = False

    return slicesAsPolygons

def vizz_2d(layer):
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches

    verts = layer


    codes = []
    codes.append(Path.MOVETO)
    for i in range((len(layer)-2)):
        codes.append(Path.LINETO)
    codes.append(Path.CLOSEPOLY)

    path = Path(verts, codes)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    patch = patches.PathPatch(path, facecolor=np.random.random(3), lw=2)
    ax.add_patch(patch)
    plt.autoscale(enable=True, axis='both', tight=None)
    plt.show()

def vizz_2d_multi(layers):
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches


    fig = plt.figure()
    ax = fig.add_subplot(111)
    for layer in layers:

        verts = layer


        codes = []
        codes.append(Path.MOVETO)
        for i in range((len(layer)-2)):
            codes.append(Path.LINETO)
        codes.append(Path.CLOSEPOLY)

        path = Path(verts, codes)



        patch = patches.PathPatch(path, facecolor=np.random.random(3), lw=2)
        ax.add_patch(patch)
    plt.autoscale(enable=True, axis='both', tight=None)
    plt.show()

def diff_layers( _subj,_clip):
    subj = pyclipper.scale_to_clipper(_subj)
    # pyclipper.SimplifyPolygon(subj)
    clip = pyclipper.scale_to_clipper(_clip)
    # pyclipper.SimplifyPolygon(clip)
    # vizz_2d(subj)
    # vizz_2d(clip)

    pc = pyclipper.Pyclipper()
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    solution = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution

def inter_layers( _subj,_clip):
    subj = pyclipper.scale_to_clipper(_subj)
    # pyclipper.SimplifyPolygon(subj)
    clip = pyclipper.scale_to_clipper(_clip)
    # pyclipper.SimplifyPolygon(clip)
    # vizz_2d(subj)
    # vizz_2d(clip)

    pc = pyclipper.Pyclipper()
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution

def intersect_layers(botLay, topLay, upskins,downskins):
    if len(botLay) == 0:
        return
    if len(topLay) == 0:
        return
    up_layer = []
    upskins.append(up_layer)
    down_layer = []
    downskins.append(down_layer)


    for pol_dex in range(len(topLay)):
        if pol_dex == 0:#is ouline
            cliped = diff_layers(botLay,topLay[pol_dex])
            for poly in cliped:
                up_layer.append(poly)
        if pol_dex >0:#is hole
            cliped = inter_layers(botLay,topLay[pol_dex])
            for poly in cliped:
                up_layer.append(poly)

    for pol_dex in range(len(botLay)):
        if pol_dex == 0:#is ouline
            # po = pyclipper.PyclipperOffset()
            # po.AddPaths(topLay,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
            # topLay_of = po.Execute(100000000)
            cliped = diff_layers(topLay,botLay[pol_dex])
            for poly in cliped:
                down_layer.append(poly)
        if pol_dex >0:#is hole
            cliped = inter_layers(topLay,botLay[pol_dex])
            for poly in cliped:
                down_layer.append(poly)

def intersect_layers_debug(botLay, topLay, upskins,downskins):
    if len(botLay) == 0:
        return
    if len(topLay) == 0:
        return
    up_layer = []
    upskins.append(up_layer)
    down_layer = []
    downskins.append(down_layer)


    for pol_dex in range(len(topLay)):
        if pol_dex == 0:#is ouline
            cliped = diff_layers(botLay,topLay[pol_dex])
            for poly in cliped:
                up_layer.append(poly)
        if pol_dex >0:#is hole
            cliped = inter_layers(botLay,topLay[pol_dex])
            for poly in cliped:
                up_layer.append(poly)


    for pol_dex in range(len(botLay)):
        if pol_dex == 0:#is ouline
            po = pyclipper.PyclipperOffset()
            po.AddPaths(topLay,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
            tutu = pyclipper._check_scaling_factor(topLay)
            topLay_of = po.Execute(100000000)
            cliped = diff_layers(topLay_of,botLay[pol_dex])
            for poly in cliped:
                down_layer.append(poly)
        if pol_dex >0:#is hole
            po = pyclipper.PyclipperOffset()
            po.AddPaths(botLay,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
            topLay_of = po.Execute(1000000)
            cliped = inter_layers(topLay_of,botLay[pol_dex])
            for poly in cliped:
                down_layer.append(poly)

    # if (len(topLay) > 0 and len(botLay) > 0):
    #     cliped = XOR_layers(topLay[0],botLay[0])
    #     for poly in cliped:
    #         down_layer.append(poly)
    #     cliped = XOR_layers(botLay[0],topLay[0])
    #     for poly in cliped:
    #         up_layer.append(poly)
    #
    #     top_holes = topLay.remove(topLay[0])
    #     for pol in top_holes:
    #         cliped = XOR_layers(pol,botLay[0])
    #         for poly in cliped:
    #             down_layer.append(poly)
    #
    #     cliped = XOR_layers(botLay[1],topLay[0])
    #     for poly in cliped:
    #         down_layer.append(poly)
    #
    #
    #     cliped = XOR_layers(botLay[0],topLay[1])
    #     for poly in cliped:
    #         up_layer.append(poly)
    #     cliped = XOR_layers(topLay[0],botLay[1])
    #     for poly in cliped:
    #         up_layer.append(poly)

def intersect_all_layers(layers):

    downskins = []
    upskins = []
    for i in range(len(layers)-1):
        if False:
            intersect_layers_debug(layers[i],layers[i+1],upskins,downskins)
        else:
            intersect_layers(layers[i],layers[i+1],upskins,downskins)

    # for layer in downskins:
    #     vizz_2d_multi(layer)
    # for layer in upskins:
    #     vizz_2d_multi(layer)
    return downskins,upskins








# def get_poly_struct(layer):
#     poly_struct = []
#     node = pyclipper.PyPolyNode()
#
#
#
#
#     for poly in layer:
#         for poly_node in poly_struct:
#             if poly1_in_poly2(poly,poly_node.contour):
#                 for child in poly_node.child:


def poly1_in_poly2(poly1,poly2):
    point = poly1[0]
    if pyclipper.PointInPolygon(point,poly2):
        return True
    else:
        return False

def reord_layers_multi_islands ( layers):
    for layer in layers:
        if len(layer)>1:
            for island in layer:

                for poly1_index in range(len(island)-1):
                    if poly1_in_poly2(island[poly1_index+1], island[poly1_index]):
                        island.insert(0,island.pop(poly1_index))
                if poly1_in_poly2(island[0], island[len(island)-1]):
                    island.insert(0,island.pop(len(island)-1))

    return layers

def reord_layers ( layers):
    for layer in layers:
        if len(layer)>1:
            for poly1_index in range(len(layer)-1):
                if poly1_in_poly2(layer[poly1_index+1], layer[poly1_index]):
                    layer.insert(0,layer.pop(poly1_index))
            if poly1_in_poly2(layer[0], layer[len(layer)-1]):
                layer.insert(0,layer.pop(len(layer)-1))
    for layer in layers:
        for poly_dex in range(len(layer)):
            if poly_dex == 0:
                if not pyclipper.Orientation(layer[poly_dex]) :
                    pyclipper.ReversePath(layer[poly_dex])
            else:
                if pyclipper.Orientation(layer[poly_dex]) :
                    pyclipper.ReversePath(layer[poly_dex])
    return layers



if __name__ == '__main__':
    import time

    start_time = time.time()
    print("--- %s seconds ---" % (time.time() - start_time))
    mesh = mesh.Mesh.from_file("cyl_cyl.stl")
    print("--- %s seconds ---" % (time.time() - start_time))
    mesh = remove_duplicates_from_mesh(mesh)
    print("--- %s seconds ---" % (time.time() - start_time))
    slice_layers = slicer_from_mesh(mesh, slice_height_from=0, slice_height_to=100, slice_step=1)
    print("--- %s seconds ---" % (time.time() - start_time))
    layers_as_polygons = polygonize_layers(slice_layers)
    for layer in layers_as_polygons:
        pyclipper.SimplifyPolygons(layer)
        pyclipper.CleanPolygons(layer)
    # tut = pyclipper.scale_to_clipper(10)
    # vizz_2d_multi(layers_as_polygons[8])
    # vizz_2d_multi(layers_as_polygons[9])
    # for i in range(len(layers_as_polygons[4])):
    #     vizz_2d(layers_as_polygons[7][i])
    # for i in range(len(layers_as_polygons[9])):
    #     vizz_2d(layers_as_polygons[16][i])
    print("--- %s seconds ---" % (time.time() - start_time))
    # reord = [layers_as_polygons[8][1],layers_as_polygons[8][0]]
    # vizz_2d_multi(reord)
    layers_as_polygons = reord_layers(layers_as_polygons)
    skins = intersect_all_layers(layers_as_polygons)
    downskins = skins[0]
    upskins = skins[1]
    for downskin in downskins:
        po = pyclipper.PyclipperOffset()
        po.AddPaths(downskin,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        offseted = po.Execute(pyclipper.scale_to_clipper(-0.2))
        vizz_2d_multi(offseted)


    # cliped_layers = XOR_layers(layers_as_polygons[9][0],layers_as_polygons[8][1])
    # cliped_layers2 = XOR_layers(layers_as_polygons[8][0],layers_as_polygons[9][1])
    # vizz_2d_multi(cliped_layers)
    # vizz_2d_multi(cliped_layers2)
    # vizz_2d_multi([cliped_layers2[0],cliped_layers[0]])
    # for i in range(len(cliped_layers)):
    #     vizz_2d(cliped_layers[i])
    # point = pyclipper.scale_to_clipper(layers_as_polygons[10][0][5])
    # poly = pyclipper.scale_to_clipper(layers_as_polygons[2][0])
    # print("--- %s seconds ---" % (time.time() - start_time))
    # isIn = pyclipper.PointInPolygon(point, poly)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("dtc")


