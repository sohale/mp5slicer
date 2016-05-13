from clipper_operations import SingleLineOffset
from Polygon_stack import *

class SingleLine():
    def __init__(self,contour, line_width):
        if (isinstance(contour,list) and len(contour) ==0) or isinstance(contour[0][0], long) or isinstance(contour[0][0], int):
            self.contour = contour
            self.width = line_width
            self.inner_bound = None
            self.outter_bound = None
        else:
            raise TypeError

    def get_contour(self):

        return self.contour

    def get_inner_bound(self):
        if self.inner_bound == None:
            self.inner_bound = Polygon_stack(SingleLineOffset(self.contour, -self.width/2))
        return self.inner_bound

    def get_outter_bound(self):
        if self.outter_bound == None:
            self.outter_bound = Polygon_stack(SingleLineOffset(self.contour, self.width/2))
        return self.outter_bound

    def offset(self,value):
        return Polygon_stack(SingleLineOffset(self.contour, value))