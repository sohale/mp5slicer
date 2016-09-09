import inspect
import os
import sys
from slicer.commons.utils import scale_line_from_clipper, scale_list_from_clipper
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.print_tree.Polygon_stack import *
import pyclipper
# A Line stack is equivalent to a polygon stack but its polygons are open
class Line_stack:
    def __init__(self, lines = None):
        if sys.version_info[0] == (3):
            if lines is None:
                self.lines = []
            elif isinstance(lines,Line_stack):
                self.lines  = lines.lines
            elif isinstance(lines, list) and len(lines) == 0:
                self.lines  = []
            elif  isinstance(lines[0][0],int):
                self.lines  = [lines]
            elif  isinstance(lines[0][0][0],int):
                self.lines = lines
            else: raise TypeError
        else:
            if lines is None:
                self.lines = []
            elif isinstance(lines,Line_stack):
                self.lines  = lines.lines
            elif isinstance(lines, list) and len(lines) == 0:
                self.lines  = []
            elif  isinstance(lines[0][0],int) or isinstance(lines[0][0], long):
                self.lines  = [lines]
            elif  isinstance(lines[0][0][0],int) or isinstance(lines[0][0][0], long):
                self.lines = lines
            else: raise TypeError

    def is_empty(self):
        if self.lines:
            return False
        else:
            return True

    def add_line(self,line):
        self.lines.append(line)

    # def get_polygons_contours(self):
    #     contours = []
    #     for line  in self.lines:
    #         contours += line.get_contour()
    #
    #     return contours

    def intersect_with(self, other):
        if self.is_empty() or other.is_empty():
            return Line_stack([])
        return Line_stack(inter_layers(self.lines,other.polygons , False))

    def combine(self, other): # danger this is not union, this is only add two linestack together
        if self.is_empty() and other.is_empty():
            return Line_stack()
        elif self.is_empty():
            return other
        elif other.is_empty():
            return self
        else:
            lines = self.lines + other.lines
            return Line_stack(lines)
        
    def difference_with(self, other):
        if other.is_empty():
            return Line_stack(self.lines) # same return format
        if self.is_empty():
            return Line_stack([])
        try:
            return Line_stack(diff_layers(self.lines,other.polygons , False))
        except:
            raise RuntimeError

    def get_print_line(self):
        if not self.is_empty():
            return scale_list_from_clipper(self.lines)
        else:
            return []
    def return_start_end_point(self):
        if self.is_empty():
            return [None, None]
        else:
            return [self.lines[0][0], self.lines[-1][-1]]

    def visualize(self):
        import matplotlib.pyplot as plt
        for each_polygon in self.lines:
            for this_vertex, next_vertex in zip(each_polygon, each_polygon[1:]):
                plt.plot([this_vertex[0],next_vertex[0]], [this_vertex[1],next_vertex[1]])
        plt.show()


    def new_line(self):
        self.lines.append([])
    def add_point_in_last_line(self, point):
        if self.lines[-1] == []:
            self.lines[-1].append(point)
        elif self.lines[-1][-1] == point:
            pass
        else:
            self.lines[-1].append(point)
    def offset_point(self, offset_value):
        points = []
        for each_line in self.lines:
            if len(each_line) == 1:
                points.append(each_line)
        sol = LinesOffset(points, offset_value)
        for each_line_index in range(len(sol)): 
            sol[each_line_index].append(sol[each_line_index][0])

        return Polygon_stack(sol)

    def offset_line(self, offset_value):
        sol = []
        #  offset for lines only
        lines = []
        for each_line in self.lines:
            if len(each_line) != 1:
                lines.append(each_line)

        sol += LinesOffset(lines, offset_value)
        return Polygon_stack(sol)

    def offset_all(self, offset_value):
        ps = Polygon_stack([])
    
        ps.add_polygon_stack(self.offset_line(0.01))
        ps.add_polygon_stack(self.offset_point(0.01))

        return ps.offset(offset_value)


    def clean(self):
        lines = []
        for each_line in self.lines:
            if len(each_line) > 1:
                lines.append(each_line)
        self.lines = lines
    def last_line_is_empty(self):
        if self.is_empty():
            raise NotImplementedError

        if self.lines[-1]:
            return False
        else:
            return True
    def point_at_last_line(self):
        return self.lines[-1][-1]

class Support_Line_Stack(Line_stack):

    def offset_point(self, offset_value):
        import slicer.print_tree.support as support
        points = []
        for each_line in self.lines:
            if len(each_line) == 1 and not isinstance(each_line[0], support.Last_point):
                points.append(each_line)
        sol = LinesOffset(points, offset_value)
        for each_line_index in range(len(sol)): 
            sol[each_line_index].append(sol[each_line_index][0])
        return Polygon_stack(sol)

    def offset_last_point(self):
        import slicer.print_tree.support as support
        points = []
        for each_line in self.lines:
            if len(each_line) == 1 and isinstance(each_line[0], support.Last_point):
                points.append(each_line[0].return_point_as_new_line())
        sol = LinesOffset(points, support.Last_point.offset_value())
        for each_line_index in range(len(sol)): 
            sol[each_line_index].append(sol[each_line_index][0])

        return Polygon_stack(sol)