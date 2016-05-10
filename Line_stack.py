from clipper_operations import *


class Line_stack():
    def __init__(self, lines = None):
        self.isEmpty = True
        if lines is None:
            self.lines = []
        elif isinstance(lines,Line_stack):
            self.lines  = lines.lines
            self.isEmpty = lines.isEmpty
        elif isinstance(lines, list) and len(lines) == 0:
            self.lines  = []
        elif isinstance(lines[0][0],long) or isinstance(lines[0][0],int):
            self.lines  = [lines]
            self.isEmpty = False
        elif isinstance(lines[0][0][0],long) or isinstance(lines[0][0][0],int):
            self.lines = lines
            self.isEmpty = False
        else: raise TypeError

    def add_line(self,line):
        self.lines.append(line)
        self.isEmpty = False

    # def get_polygons_contours(self):
    #     contours = []
    #     for line  in self.lines:
    #         contours += line.get_contour()
    #
    #     return contours

    def intersect_with(self, other):
        if self.isEmpty or other.isEmpty:
            return []
        return inter_layers(self.lines,other.polygons , False)

    def union_with(self, other):
        pass

    def difference_with(self, other):
        if self.isEmpty or other.isEmpty:
            return []
        try:
            return diff_layers(self.lines,other.polygons , False)
        except:
            print("svsghsibiwcwsl")