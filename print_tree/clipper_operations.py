import pyclipper
import inspect, os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from slicer.commons.utils import scale_value_to_clipper



def diff_layers( _subj,_clip,closed):


    pc = pyclipper.Pyclipper()
    pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        raise RuntimeError

    if closed:
        solution = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    else:
        solution = pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        solution = pyclipper.PolyTreeToPaths(solution)

    return solution

def union_layers( _subj,_clip,closed):


    pc = pyclipper.Pyclipper()
    pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        raise RuntimeError

    if closed:
        solution = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    else:
        solution = pc.Execute2(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        solution = pyclipper.PolyTreeToPaths(solution)

    return solution

def union_itself( _subj,closed):


    pc = pyclipper.Pyclipper()
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        raise RuntimeError

    if closed:
        solution = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    else:
        # solution = pc.Execute2(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        # solution = pyclipper.PolyTreeToPaths(solution)
        raise NotImplementedError

    return solution

# def union_layers_polytree( _subj,_clip,closed):
#
#
#     pc = pyclipper.Pyclipper()
#     pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
#     try:
#         pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
#     except:
#         raise RuntimeError
#
#     return pc.Execute2(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)


def diff_layers_as_polytree( _subj,_clip,closed):
    pc = pyclipper.Pyclipper()
    pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        raise RuntimeError

    solution = pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution


def inter_layers( _subj,_clip,closed):
    if len(_clip) == 0 :
        return []
    pc = pyclipper.Pyclipper()
    try:
        pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
    except:
        raise RuntimeError

    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        raise RuntimeError

    if closed:
        solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    else:
        solution = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        solution = pyclipper.PolyTreeToPaths(solution)

    return solution

def inter_layers_as_polytree( _subj,_clip,closed):

    pc = pyclipper.Pyclipper()

    pc.AddPaths(_clip, pyclipper.PT_CLIP, True)

    pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)

    solution = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution

def isPaths(paths):
    assert(isinstance(paths[0][0][0], int))


def offset_default(polygon_stack,val):
    path = polygon_stack.polygons
    po = pyclipper.PyclipperOffset()
    po.AddPaths(path,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)


    offseted = po.Execute(scale_value_to_clipper(val))

    return offseted

# @profile
def offset(polygon_stack,val):
    path = polygon_stack.polygons
    # path = pyclipper.ReversePaths(polygon_stack.polygons)
    # for polygon_index in range(len(path)):
    #     if not pyclipper.Orientation(path[polygon_index]):
    #         path[polygon_index] = pyclipper.ReversePath(path[polygon_index])
    po = pyclipper.PyclipperOffset()
    po.AddPaths(path,pyclipper.JT_MITER,pyclipper.ET_CLOSEDPOLYGON)

    offseted = po.Execute(scale_value_to_clipper(val))

    return offseted

def SinglePolygonOffset(single_line,val):
    path = single_line
    # path = pyclipper.ReversePaths(polygon_stack.polygons)
    # for polygon_index in range(len(path)):
    #     if not pyclipper.Orientation(path[polygon_index]):
    #         path[polygon_index] = pyclipper.ReversePath(path[polygon_index])
    po = pyclipper.PyclipperOffset()
    po.AddPath(path,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)


    offseted = po.Execute(scale_value_to_clipper(float(val)))

    return offseted


# def diff_layers_as_path( _subj,_clip):
#
#     # if not multiple_paths:
#     #     _subj = [_subj,]
#
#     pc = pyclipper.Pyclipper()
#     pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
#     try:
#         pc.AddPaths(_subj, pyclipper.PT_SUBJECT, True)
#     except:
#         print("sgs")
#
#     solution = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
#
#     return solution


# def inter_layers_as_path( _subj,_clip):
#
#
#     pc = pyclipper.Pyclipper()
#     try:
#         pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
#     except:
#         print("dsgs")
#     try:
#         pc.AddPaths(_subj, pyclipper.PT_SUBJECT, True)
#     except:
#         print("bubu")
#
#     solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
#
#     return solution


# def intersect_layers_new(botLay,thisLay, topLay):
#     upskins = []
#     downskins= []
#
#     pc = pyclipper.Pyclipper()
#     try:
#         pc.AddPaths(topLay, pyclipper.PT_CLIP, True)
#     except:
#         print("dsgs")
#     try:
#         pc.AddPaths(thisLay, pyclipper.PT_SUBJECT, True)
#     except:
#         print("bubu")
#
#     solution = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
#     # util.vizz_2d_multi(solution)
#
#     return solution

def LinesOffset(lines, offset_value,does_visualize=False):

    pc = pyclipper.PyclipperOffset()
    pc.AddPaths(lines, pyclipper.JT_SQUARE, pyclipper.ET_OPENSQUARE)

    solution = pc.Execute(scale_value_to_clipper(offset_value))
    # solution = pyclipper.scale_from_clipper(solution)

    if does_visualize:
        import matplotlib.pyplot as plt 
        for line in lines:
            plt.plot([i[0] for i in line], [i[1] for i in line])

        for line in solution:
            plt.plot([i[0] for i in line], [i[1] for i in line])
            plt.plot([line[-1][0],line[0][0]],[line[-1][1],line[0][1]])
        plt.show()

    return solution

def main():
    pass

if __name__ == '__main__':
    main()

