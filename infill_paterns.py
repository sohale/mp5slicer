import numpy


def linear_infill(spacing,XorY,BBox):
    _min = min(BBox[0],BBox[2])
    _max = max(BBox[1],BBox[3])
    length_min = min(BBox[0],BBox[2])
    length_max = max(BBox[1],BBox[3])
    lines = []
    vals = numpy.arange(_min,_max,spacing)
    if XorY == 0:
        for val in vals:
            lines.append(((val,length_min),(val,length_max)))
    else:
        for val in vals:
            lines.append(((length_min,val),(length_max,val)))
    return lines
