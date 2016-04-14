from Skins import *
from  slicer import *



def polygonize_layers_from_trimed_dict(slice_layers):

    for slice in slice_layers:

        for bipoint in slice:
            if len(slice[bipoint]) != 2:
                print(bipoint," : ",slice[bipoint])

    slicesAsPolygons = []
    for slicee in slice_layers:
        polygons = []
        slicesAsPolygons.append(polygons)
        slicekeys = set(slicee.keys())

        while True:
            try:
                start = slicekeys.pop()
            except KeyError:
                break

            end = slicee[start][0]

            newPolygon = []
            first_point = start
            polygons.append(newPolygon)

            newPolygon.append(start)
            newPolygon.append(end)
            continuePolygon = True
            # Is there a new line i the polygon
            while continuePolygon:
                previous_neighbour = start

                start = end
                try:
                    slicekeys.remove(end)
                except:
                    # pass
                    print("yefy")

                end = slicee[start][0]
                if end == previous_neighbour:

                    end = slicee[start][1]


                if end == first_point:
                    continuePolygon = False
                else:
                    newPolygon.append(end)

    return slicesAsPolygons


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
    slice_layers = slicer_from_mesh_as_dict(mesh, slice_height_from=0, slice_height_to=100, slice_step=1)
    print("--- %s seconds ---" % (time.time() - start_time))
    layers_as_polygons = polygonize_layers_from_trimed_dict(slice_layers)
    print("--- %s seconds ---" % (time.time() - start_time))
    for layer in layers_as_polygons:
        vizz_2d_multi(layer)
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
    for skin_index in range(len(downskins)):
        po = pyclipper.PyclipperOffset()
        po.AddPaths(downskins[skin_index],pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        downskins[skin_index] = po.Execute(pyclipper.scale_to_clipper(-0.5))

    for downskin in downskins:

        vizz_2d_multi(downskin)


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


