import pyclipper
import utils as util
from Island_stack import *


def diff_layers( _subj,_clip,closed):

    pc = pyclipper.Pyclipper()
    pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        print("sgs")

    if closed:
        solution = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    else:
        solution = pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        solution = pyclipper.PolyTreeToPaths(solution)

    return solution

def diff_layers_as_polytree( _subj,_clip,closed):

    pc = pyclipper.Pyclipper()
    pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        print("sgs")

    solution = pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution


def inter_layers( _subj,_clip,closed):

    pc = pyclipper.Pyclipper()
    try:
        pc.AddPaths(_clip, pyclipper.PT_CLIP, True)
    except:
        print("ysgfsfssffy")


    pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)

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


def offset(path,val):
    # path = pyclipper.scale_to_clipper(path)
    po = pyclipper.PyclipperOffset()
    po.AddPath(path,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
    offseted = po.Execute(pyclipper.scale_to_clipper(val))
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


