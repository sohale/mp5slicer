
from slicer.Polygon_stack import *

#Polyon are generaly stored as complex polygon types
class Line():
    def __init__(self,contour, line_width):
        assert(isinstance(contour, Polygon_stack))
        self.width = line_width
        # self.midle_line
        self.inner_bound = None
        self.outter_bound = None
        self.contour = contour


    def get_contour(self):

        return self.contour

    def get_inner_bound(self):
        if self.inner_bound == None:
            self.inner_bound = Polygon_stack(offset(self.contour, -self.width/2))
        return self.inner_bound

    def get_outter_bound(self):
        if self.outter_bound == None:
            self.outter_bound = Polygon_stack(offset(self.contour, self.width/2))
        return self.outter_bound
