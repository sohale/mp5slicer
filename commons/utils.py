import sys
from math import sqrt,pow

from slicer.print_tree.clipper_operations import *
import pyclipper

def scale_list_to_clipper(array): # faster then pyclipper.scale_to_clipper
    def scale_list(l):
        return [[int(i[0]*(2**32)/2), int(i[1]*(2**32)/2)] for i in l]
    return list(map(scale_list, array))

def scale_point_to_clipper(point):
    return [int(point[0]*(2**32)/2), int(point[1]*(2**32)/2)]

def scale_line_to_clipper(array): # faster then pyclipper.scale_to_clipper
    return list(map(scale_point, array))

def scale_value_to_clipper(val):  # faster then pyclipper.scale_to_clipper
    return int(val*(2**32)/2)

is_64bits = sys.maxsize > 2**32
if not is_64bits:
    scale_list_to_clipper = pyclipper.scale_to_clipper
    scale_point_to_clipper = pyclipper.scale_to_clipper
    scale_line_to_clipper = pyclipper.scale_to_clipper
    scale_value_to_clipper = pyclipper.scale_to_clipper

def copy_module(module):
    copy = conf_module
    attributes = dir(module)
    for atr in attributes:
        setattr(copy,atr, getattr(module,atr))
    return copy

class conf_module:
    def __init__(self):
        pass

def get_center(BBox):
    x = BBox[2] - BBox[0]
    y = BBox[1] - BBox[3]
    return (x,y)

# clipper gives the following format for bounding box
# rectangle[0] : left
# rectangle[1] : top
# rectangle[2] : right
# rectangle[3] : bottom
def overlap(bb1, bb2):
    return not ( bb2[0] > bb1[2] or bb2[2] < bb1[0] or bb2[1] > bb1[3] or bb2[3] < bb1[1])

def does_bounding_box_intersect(RectA, RectB):

    if RectA == None or RectB == None:
        return True
    try:
        RectA.xmin < RectB.xmax 
    except TypeError:
        print(RectA.xmin)
        print(RectB.xmax)
        
    if (RectA.xmin < RectB.xmax and \
        RectA.xmax > RectB.xmin and \
        RectA.ymax < RectB.ymin and \
        RectA.ymin > RectB.ymax):
        return True
    else:
        return False



def getPath(bound, holes,path):
    pc = pyclipper.Pyclipper()
    pc.AddPath(path, pyclipper.PT_SUBJECT, False)
    pc.AddPath(bound, pyclipper.PT_CLIP, True)
    result = pyclipper.PolyTreeToPaths(pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
    resultSize = len(result)
    if resultSize == 1:#cross once the bound
        middlePoint = getMiddlePoint([result[0][0],result[0][1]])
        vetctor = getVector([result[0][0],result[0][1]])
        point = getInsidePoint(middlePoint,vetctor,bound)
        return getPath(bound,holes,[path[0],point]) + getPath(bound,holes,[point,path[1]])[1:]
    elif resultSize > 1:#cross multiple times the bound
        middlePoint = None
        solution = [path[0]]
        previousMiddlePoint = path[0]
        for i in range(0,resultSize-1):
            middlePoint = getMiddlePoint([result[i][1],result[i+1][0]])
            vetctor = getVector([result[i][1],result[i+1][0]])
            for hole in holes:
                if pyclipper.PointInPolygon(middlePoint,hole):
                    middlePoint = getOutsidePoint(middlePoint,vetctor,hole)
                    break
            solution += getPath(bound,holes,[previousMiddlePoint,middlePoint])[1:]
            previousMiddlePoint = middlePoint
        solution += getPath(bound, holes, [previousMiddlePoint, path[1]])[1:]
        return solution

    pc.Clear()
    pc.AddPath(path, pyclipper.PT_SUBJECT, False)
    for hole in holes:
        pc.AddPath(hole, pyclipper.PT_CLIP, True)
    result = pyclipper.PolyTreeToPaths(pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
    resultSize = len(result)
    if(resultSize==2):#cross only one hole once
        for hole in holes:# seek the crossing hole
            pc.Clear()
            pc.AddPath(path, pyclipper.PT_SUBJECT, False)
            pc.AddPath(hole, pyclipper.PT_CLIP, True)
            result = pyclipper.PolyTreeToPaths(pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
            resultSize = len(result)
            if resultSize == 2:
                middlePoint = getMiddlePoint([result[0][1], result[1][0]])
                vetctor = getVector([result[0][1], result[1][0]])
                point = getOutsidePoint(middlePoint, vetctor, hole)
                return getPath(bound, holes, [path[0], point]) + getPath(bound, holes, [point, path[1]])[1:]

    elif(resultSize > 2):#cross multipleholes or one hole multiple times
        middlePoint = None
        solution = [path[0]]
        previousMiddlePoint = path[0]
        for i in range(1, resultSize - 1):
            middlePoint = getMiddlePoint([result[i][0], result[i][1]])
            solution += getPath(bound, holes, [previousMiddlePoint, middlePoint])[1:]
            previousMiddlePoint = middlePoint
        solution += getPath(bound, holes, [previousMiddlePoint, path[1]])[1:]
        return solution


    return path

def getMiddlePoint(points):
    return [(points[0][0]/2)+(points[1][0]/2),(points[0][1]/2)+(points[1][1]/2)]

def getVector(points):
    val = sqrt(pow(points[0][0] - points[1][0],2) + pow(points[0][1] - points[1][1],2))
    return [scale_value_to_clipper((points[0][1] - points[1][1])/val)*0.1, scale_value_to_clipper((points[1][0] - points[0][0])/val)*0.1]

def getInsidePoint(startPoint,vect,polygon):
    point = startPoint
    reversePoint = startPoint
    soluce = None
    while soluce == None :
        point = [point[0]+vect[0],point[1]+vect[1]]
        if pyclipper.PointInPolygon(point,polygon):
            return point
        reversePoint = [reversePoint[0] - vect[0], reversePoint[1] - vect[1]]
        if pyclipper.PointInPolygon(reversePoint, polygon):
            return reversePoint

def getOutsidePoint(startPoint,vect,polygon):
    point = startPoint
    reversePoint = startPoint
    soluce = None
    while soluce == None :
        point = [point[0]+vect[0],point[1]+vect[1]]
        if not pyclipper.PointInPolygon(point,polygon):
            return point
        reversePoint = [reversePoint[0] - vect[0], reversePoint[1] - vect[1]]
        if not pyclipper.PointInPolygon(reversePoint, polygon):
            return reversePoint

def polygonize_layers_from_trimed_dict(slice_layers):

    for slice_index in range(len(slice_layers)):
        # sys.stderr.write(slice_index)

        for bipoint in slice_layers[slice_index]:
            if len(slice_layers[slice_index][bipoint]) != 2:
                sys.stderr.write(str(bipoint)+" : "+str(slice_layers[slice_index][bipoint]) +" : " + str(slice_index)+ "\n")


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
                    raise RuntimeError

                end = slicee[start][0]
                if end == previous_neighbour:

                    end = slicee[start][1]


                if end == first_point:
                    continuePolygon = False
                else:
                    newPolygon.append(end)

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

def vizz_2d_multi(layers,img):
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



        patch = patches.PathPatch(path,fill=False, facecolor=None, lw=2)
        ax.add_patch(patch)
    plt.autoscale(enable=True, axis='both', tight=None)
    plt.show()
    plt.savefig(img)

def visualise_polygon_list(polygon_list, obb):
    import matplotlib.pyplot as plt
    print(polygon_list)
    first_polygon = polygon_list[0]
    for i, j in zip(first_polygon, first_polygon[1:]):
        plt.plot([i[0],j[0]], [i[1], j[1]])


    attr = ['left', 'right', 'top','bottom'] 
    print(obb)
    plt.plot( obb.left, obb.bottom, 'o')
    plt.plot(obb.right, obb.bottom, 'o')
    plt.plot( obb.left, obb.top, 'o')
    plt.plot(obb.right, obb.top, 'o')

    plt.show()
    raise Tiger

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

def distance(point1, point2):
    return sqrt(pow((point1[0]-point2[0]),2) + pow((point1[1]-point2[1]),2))

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
    # print("--- %s seconds ---" % (time.time() - start_time))
    mesh = mesh.Mesh.from_file("cyl_cyl.stl")
    # print("--- %s seconds ---" % (time.time() - start_time))
    mesh = remove_duplicates_from_mesh(mesh)
    # print("--- %s seconds ---" % (time.time() - start_time))
    slice_layers = slicer_from_mesh_as_dict(mesh, slice_height_from=0, slice_height_to=100, slice_step=1)
    # print("--- %s seconds ---" % (time.time() - start_time))
    layers_as_polygons = polygonize_layers_from_trimed_dict(slice_layers)
    # print("--- %s seconds ---" % (time.time() - start_time))
    for layer in layers_as_polygons:
        vizz_2d_multi(layer)
    # tut = pyclipper.scale_to_clipper(10)
    # vizz_2d_multi(layers_as_polygons[8])
    # vizz_2d_multi(layers_as_polygons[9])
    # for i in range(len(layers_as_polygons[4])):
    #     vizz_2d(layers_as_polygons[7][i])
    # for i in range(len(layers_as_polygons[9])):
    #     vizz_2d(layers_as_polygons[16][i])
    # print("--- %s seconds ---" % (time.time() - start_time))
    # reord = [layers_as_polygons[8][1],layers_as_polygons[8][0]]
    # vizz_2d_multi(reord)
    layers_as_polygons = reord_layers(layers_as_polygons)
    skins = intersect_all_layers(layers_as_polygons)
    downskins = skins[0]
    upskins = skins[1]
    for skin_index in range(len(downskins)):
        po = pyclipper.PyclipperOffset()
        po.AddPaths(downskins[skin_index],pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        downskins[skin_index] = po.Execute(scale_value_to_clipper(-0.5))

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
    # print("--- %s seconds ---" % (time.time() - start_time))



