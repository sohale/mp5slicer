from clipper_operations import *


class Line_stack():
    def __init__(self, lines = None):
        if lines is None:
            self.lines = []
        else:
            self.lines = lines

    def add_line(self,line):
        self.lines.append(line)

    # def get_polygons_contours(self):
    #     contours = []
    #     for line  in self.lines:
    #         contours += line.get_contour()
    #
    #     return contours

    def intersect_with(self, other):
        return inter_layers(self.lines,other.polygons , False)

    def union_with(self, other):
        pass

    def difference_with(self, other):
        try:
            return diff_layers(self.lines,other.polygons , False)
        except:
            print("svsghsibiwcwsl")