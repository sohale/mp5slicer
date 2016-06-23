import numpy
import math
import random

def linear_infill(spacing,XorY,BBox):
    _min = min(BBox.xmin,BBox.ymin)
    _max = max(BBox.xmax,BBox.ymax)
    length_min = min(BBox.xmin,BBox.ymin)
    length_max = max(BBox.xmax,BBox.ymax)
    lines = []
    vals = numpy.arange(_min,_max,spacing)
    if XorY == 0:
        for val in vals:
            lines.append(((val,length_min),(val,length_max)))
    else:
        for val in vals:
            lines.append(((length_min,val),(length_max,val)))
    return lines



def linear_infill2(spacing,teta,BBox):

    teta = teta * math.pi / 180

    # In the folowing, we will generate infill lines in the given bounding box.
    # To make things more easy , these lines will partially be generated outside the bounding box.
    # We want to generate only one line, that will be used to create all the lines by an offset that is constant.
    #
    # We will considere the circle that contains the bounding box.
    # This circle is usefull to generate the initial line and to determine how many times the line has to e offseted.

    lines = []

    radius = dist((BBox.xmax,BBox.ymax), (BBox.xmin, BBox.ymin)) / 2.0
    center = (BBox.xmin + (BBox.xmax - BBox.xmin)/float(2)), (BBox.ymin + (BBox.ymax - BBox.ymin)/2.0)

    # first we get an horizontal
    init_point_1 = [radius * math.cos(teta) + center[0], radius * math.sin(teta)+ center[1]]
    init_point_2 = [radius * math.cos(teta + math.pi)+ center[0], radius * math.sin(teta + math.pi)+ center[1]]
    init_line = (init_point_1, init_point_2)
    lines.append(init_line)

    # d is the distance between each line
    d = spacing
    positive_offset = [d * math.cos(teta + math.pi/2), d* math.sin(teta+ math.pi/2)]

    point_1 = [(init_point_1[0] + positive_offset[0]) , (init_point_1[1] + positive_offset[1])]
    point_2 = [(init_point_2[0] + positive_offset[0]), (init_point_2[1] + positive_offset[1])]
    line = [point_1, point_2]
    lines.append(line)

    # offset_count is the number of times the line has to be offseted positively or negatively
    offset_count = int(radius / d)
    for i in range(offset_count):
        point_1 = [(point_1[0] + positive_offset[0]), (point_1[1] + positive_offset[1])]
        point_2 = [(point_2[0] + positive_offset[0]), (point_2[1] + positive_offset[1])]
        line = [point_1, point_2]
        lines.append(line)

    # we do the same in the other direction
    negative_offset = (- positive_offset[0], -positive_offset[1])

    point_1 = [(init_point_1[0] + negative_offset[0]), (init_point_1[1] + negative_offset[1])]
    point_2 = [(init_point_2[0] + negative_offset[0]), (init_point_2[1] + negative_offset[1])]
    line = [point_1, point_2]
    lines.append(line)

    # offset_count is the number of times the line has to be offseted positively or negatively
    offset_count = int(radius / d)
    for i in range(offset_count):
        point_1 = [(point_1[0] + negative_offset[0]), (point_1[1] + negative_offset[1])]
        point_2 = [(point_2[0] + negative_offset[0]), (point_2[1] + negative_offset[1])]
        line = [point_1, point_2]
        lines.append(line)

    return lines





def dist(point1, point2):
    return math.sqrt(pow((point1[0]-point2[0]),2) + pow((point1[1]-point2[1]),2))
