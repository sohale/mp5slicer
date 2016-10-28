import math

import numpy

from mp5slicer.commons.utils import distance


def linear_infill(spacing, x_or_y, bounding_box):
    _min = min(bounding_box.xmin, bounding_box.ymin)
    _max = max(bounding_box.xmax, bounding_box.ymax)
    length_min = min(bounding_box.xmin, bounding_box.ymin)
    length_max = max(bounding_box.xmax, bounding_box.ymax)
    lines = []
    vals = numpy.arange(_min, _max, spacing)
    if x_or_y == 0:
        for val in vals:
            lines.append(((val, length_min), (val, length_max)))
    else:
        for val in vals:
            lines.append(((length_min, val), (length_max, val)))
    return lines


def linear_infill2(spacing, teta, bounding_box):

    teta = teta * math.pi / 180
    '''
    In the folowing, we will generate infill lines in the given bounding box.

    To make things more easy,
    these lines will partially be generated outside the bounding box.

    We want to generate only one line,
    that will be used to create all the lines by an offset that is constant.

    We will considere the circle that contains the bounding box.

    This circle is usefull to generate the initial line and to determine
    how many times the line has to e offseted.
    '''
    lines = []

    radius = distance((bounding_box.xmax, bounding_box.ymax),
                      (bounding_box.xmin, bounding_box.ymin)) / 2.0
    center = (bounding_box.xmin + (bounding_box.xmax - bounding_box.xmin)/2.0), \
             (bounding_box.ymin + (bounding_box.ymax - bounding_box.ymin)/2.0)

    # first we get an horizontal
    init_point_1 = [radius * math.cos(teta) + center[0],
                    radius * math.sin(teta) + center[1]]

    init_point_2 = [radius * math.cos(teta + math.pi) + center[0],
                    radius * math.sin(teta + math.pi) + center[1]]

    init_line = (init_point_1, init_point_2)
    lines.append(init_line)

    # d is the distance between each line
    d = spacing
    positive_offset = [d * math.cos(teta + math.pi/2),
                       d * math.sin(teta + math.pi/2)]
    point_1 = [(init_point_1[0] + positive_offset[0]),
               (init_point_1[1] + positive_offset[1])]
    point_2 = [(init_point_2[0] + positive_offset[0]),
               (init_point_2[1] + positive_offset[1])]

    line = [point_1, point_2]
    lines.append(line)

    # offset_count is the number of times the line has to be offseted positively or negatively
    offset_count = int(radius / d)
    for i in range(offset_count):
        point_1 = [(point_1[0] + positive_offset[0]),
                   (point_1[1] + positive_offset[1])]
        point_2 = [(point_2[0] + positive_offset[0]),
                   (point_2[1] + positive_offset[1])]
        line = [point_1, point_2]
        lines.append(line)

    # we do the same in the other direction
    negative_offset = (- positive_offset[0], -positive_offset[1])
    point_1 = [(init_point_1[0] + negative_offset[0]),
               (init_point_1[1] + negative_offset[1])]
    point_2 = [(init_point_2[0] + negative_offset[0]),
               (init_point_2[1] + negative_offset[1])]
    line = [point_1, point_2]
    lines.append(line)

    # offset_count is the number of times the line has to be offseted positively or negatively
    offset_count = int(radius / d)
    for i in range(offset_count):
        point_1 = [(point_1[0] + negative_offset[0]),
                   (point_1[1] + negative_offset[1])]
        point_2 = [(point_2[0] + negative_offset[0]),
                   (point_2[1] + negative_offset[1])]
        line = [point_1, point_2]
        lines.append(line)

    return lines
