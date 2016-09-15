from slicer.print_tree.Polygon_stack import *


class SingleLine(object):
    def __init__(self, contour, line_width):
        if (isinstance(contour, list) and len(contour) == 0) or \
                isinstance(contour[0][0], int) or isinstance(contour[0][0], long):
            self.contour = contour
            self.width = line_width
            self.inner_bound = None
            self.outter_bound = None
        else:
            raise TypeError

    def get_contour(self):
        return self.contour

    def get_inner_bound(self):
        if self.inner_bound is None:
            self.inner_bound = \
                PolygonStack(single_polygon_offset(self.contour, -self.width/2))
        return self.inner_bound

    def get_outter_bound(self):
        if self.outter_bound is None:
            self.outter_bound = \
                PolygonStack(single_polygon_offset(self.contour, self.width/2))
        return self.outter_bound

    def offset(self, value):
        return PolygonStack(single_polygon_offset(self.contour, value))
