from stl_read import *
from  slicer import *
import pyclipper

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
    patch = patches.PathPatch(path, facecolor='orange', lw=2)
    ax.add_patch(patch)
    plt.autoscale(enable=True, axis='both', tight=None)
    plt.show()

def XOR_layers(_clip, _subj):
    subj = pyclipper.scale_to_clipper((_subj,))
    pyclipper.SimplifyPolygon(subj)
    clip = pyclipper.scale_to_clipper(_clip)
    pyclipper.SimplifyPolygon(clip)
    # vizz_2d(subj)
    # vizz_2d(clip)

    pc = pyclipper.Pyclipper()
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    solution = pc.Execute(pyclipper.CT_XOR, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution

if __name__ == '__main__':
    mesh = mesh.Mesh.from_file("halfsphere.stl")
    mesh = remove_duplicates_from_mesh(mesh)
    slice_layers = slicer_from_mesh(mesh, slice_height_from=0, slice_height_to=100, slice_step=1)
    layers_as_polygons = polygonize_layers(slice_layers)
    cliped_layers = XOR_layers(layers_as_polygons[1][0],layers_as_polygons[10][0])
    for i in range(len(cliped_layers)):
        vizz_2d(cliped_layers[i])

