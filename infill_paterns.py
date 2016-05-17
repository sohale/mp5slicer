import numpy


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
