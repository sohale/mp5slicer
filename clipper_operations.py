import pyclipper
import utils as util
from Island_stack import *


def diff_layers( _subj,_clip,closed):
    # subj = pyclipper.scale_to_clipper(_subj)
    # pyclipper.SimplifyPolygon(subj)
    # clip = pyclipper.scale_to_clipper(_clip)
    # pyclipper.SimplifyPolygon(clip)
    # vizz_2d(subj)
    # vizz_2d(clip)



    pc = pyclipper.Pyclipper()
    pc.AddPath(_clip, pyclipper.PT_CLIP, True)
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        print("sgs")

    solution = pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution


def diff_layers_as_path( _subj,_clip,closed,multiple_paths):
    # subj = pyclipper.scale_to_clipper(_subj)
    # pyclipper.SimplifyPolygon(subj)
    # clip = pyclipper.scale_to_clipper(_clip)
    # pyclipper.SimplifyPolygon(clip)
    # vizz_2d(subj)
    # vizz_2d(clip)

    # if len(_subj) == 0 or len( _clip) == 0:
    #     return []
    if not multiple_paths:
        _subj = [_subj,]

    pc = pyclipper.Pyclipper()
    pc.AddPath(_clip, pyclipper.PT_CLIP, True)
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        print("sgs")

    solution = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution

def inter_layers( _subj,_clip,closed):
    # subj = pyclipper.scale_to_clipper(_subj)
    # pyclipper.SimplifyPolygon(subj)
    # clip = pyclipper.scale_to_clipper(_clip)
    # pyclipper.SimplifyPolygon(clip)
    # vizz_2d(subj)
    # vizz_2d(clip)

    pc = pyclipper.Pyclipper()
    try:
        pc.AddPath(_clip, pyclipper.PT_CLIP, True)
    except:
        print("dsgs")

    pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)

    solution = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution

def inter_layers_as_path( _subj,_clip,closed):
    # subj = pyclipper.scale_to_clipper(_subj)
    # pyclipper.SimplifyPolygon(subj)
    # clip = pyclipper.scale_to_clipper(_clip)
    # pyclipper.SimplifyPolygon(clip)
    # vizz_2d(subj)
    # vizz_2d(clip)

    pc = pyclipper.Pyclipper()
    try:
        pc.AddPath(_clip, pyclipper.PT_CLIP, True)
    except:
        print("dsgs")
    try:
        pc.AddPaths(_subj, pyclipper.PT_SUBJECT, closed)
    except:
        print("bubu")

    solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

    return solution

def intersect_layers(index, botLay, topLay, upskins,downskins):
    if len(botLay) == 0:
        upskins[index] = []
        downskins[index] = []
        return
    if len(topLay) == 0:
        upskins[index] = []
        downskins[index] = []
        return
    up_layer = []
    upskins[index] = up_layer
    down_layer = []
    downskins[index] = down_layer


    for pol_dex in range(len(topLay)):
        if pol_dex == 0:#is ouline
            cliped = diff_layers(botLay,topLay[pol_dex])
            for poly in cliped:
                up_layer.append(poly)
        if pol_dex >0:#is hole
            cliped = inter_layers(botLay,topLay[pol_dex])
            for poly in cliped:
                up_layer.append(poly)

def offset(path,val):
    # path = pyclipper.scale_to_clipper(path)
    po = pyclipper.PyclipperOffset()
    po.AddPath(path,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
    offseted = po.Execute(pyclipper.scale_to_clipper(val))
    return offseted

def intersect_layers_as_island_stack( botLay,thisLay, topLay):
    upskins = []
    downskins= []
    # if len(botLay) == 0:
    #     return downskins,upskins
    # if len(topLay) == 0:
    #     return downskins,upskins







    for pol_dex in range(len(topLay)):
        if pol_dex == 0:#is ouline
            clip = offset(topLay[pol_dex], 0.2)
            # try:
            if len(clip) != 0:
                cliped = diff_layers(thisLay,clip[0],True)

            else:
                cliped = pyclipper.PyPolyNode()

            island_stack = Island_stack(cliped).islands
            upskins += island_stack
        if pol_dex >0:#is hole
            clip = offset(topLay[pol_dex],-0.2)
            # try:
            if len(clip) != 0:
                cliped = inter_layers(thisLay,clip[0],True)
            else:
                cliped = pyclipper.PyPolyNode()

            island_stack = Island_stack(cliped).islands
            upskins += island_stack

    for pol_dex in range(len(botLay)):
        if pol_dex == 0:#is ouline
            clip = offset(botLay[pol_dex],0.2)
            if len(clip) != 0:
                cliped = diff_layers(thisLay,clip[0],True)
            else:
                cliped = pyclipper.PyPolyNode()

            island_stack = Island_stack(cliped).islands
            downskins += island_stack
        if pol_dex >0:#is hole
            clip = offset(botLay[pol_dex],-0.2)
            if len(clip) != 0:
                cliped = inter_layers(thisLay,clip[0], True)

            else:
                cliped = pyclipper.PyPolyNode()

            island_stack = Island_stack(cliped).islands
            downskins += island_stack

    skins = downskins + upskins
    return skins

def intersect_layers_PT( botLay,thisLay, topLay):
    upskins = []
    downskins= []
    # if len(botLay) == 0:
    #     return downskins,upskins
    # if len(topLay) == 0:
    #     return downskins,upskins







    for pol_dex in range(len(topLay)):
        if pol_dex == 0:#is ouline
            clip = offset(topLay[pol_dex], 0.2)
            # try:
            if len(clip) != 0:
                cliped = diff_layers_as_path(thisLay,clip[0],True, True)
            else:
                cliped = []
            # except:
            #     print("dibivx")
            for poly in cliped:
                upskins.append(poly)
        if pol_dex >0:#is hole
            clip = offset(topLay[pol_dex],-0.2)
            # try:
            if len(clip) != 0:
                cliped = inter_layers_as_path(thisLay,clip[0],True)
            else:
                cliped = []
            # except:
            #     print("igsugsi")
            for poly in cliped:
                upskins.append(poly)

    for pol_dex in range(len(botLay)):
        if pol_dex == 0:#is ouline
            clip = offset(botLay[pol_dex],0.2)
            if len(clip) != 0:
                cliped = diff_layers_as_path(thisLay,clip[0],True, True)
            else:
                cliped = []

            for poly in cliped:
                downskins.append(poly)
        if pol_dex >0:#is hole
            clip = offset(botLay[pol_dex],-0.2)
            if len(clip) != 0:
                cliped = inter_layers_as_path(thisLay,clip[0], True)

            else:
                cliped = []
            for poly in cliped:
                downskins.append(poly)
    util.vizz_2d_multi(downskins)

    skins = downskins + upskins
    return skins

def intersect_layers_debug(index,botLay, topLay, upskins,downskins):
    if len(botLay) == 0:
        upskins[index] = []
        downskins[index] = []
        return
    if len(topLay) == 0:
        upskins[index] = []
        downskins[index] = []
        return
    up_layer = []
    upskins[index] = up_layer
    down_layer = []
    downskins[index] = down_layer


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


def intersect_all_layers(layers):

    downskins = [None]*len(layers)
    upskins = [None]*len(layers)
    for i in range(len(layers)-1):
        if False:
            intersect_layers_debug(layers[i],layers[i+1],upskins,downskins)
        else:
            intersect_layers(i,layers[i],layers[i+1],upskins,downskins)
    for downskin_index in range(len(downskins)):
        po = pyclipper.PyclipperOffset()
        po.AddPaths(downskins[downskin_index],pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        downskins[downskin_index] = po.Execute(pyclipper.scale_to_clipper(-0.4))

    for upskin_index in range(len(upskins)):
        po = pyclipper.PyclipperOffset()
        po.AddPaths(upskins[upskin_index],pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        upskins[upskin_index] = po.Execute(pyclipper.scale_to_clipper(-0.4))

    # for layer in downskins:
    #     vizz_2d_multi(layer)
    # for layer in upskins:
    #     vizz_2d_multi(layer)

    # extend_downskins(downskins)
    downskins = pyclipper.scale_from_clipper(downskins)
    # extend_upkins(upskins)
    upskins = pyclipper.scale_from_clipper(upskins)

    return downskins,upskins

def extend_downskins(downskins):
    skin_indexes = []
    for i in range(len(downskins)):
        if len(downskins[i]) != 0 and i<len(downskins)-1:
            skin_indexes.append(i)

    for index in skin_indexes:
        pass
        # downskins[index+1].append(downskins[index])

def extend_upkins(upskins):
    for i in range(len(upskins)):
        if len(upskins[i]) != 0 and i>1:
            upskins[i-1].append(upskins[i])