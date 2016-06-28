from slicer.clipper_operations import *
import pyclipper

# A Line stack is equivalent to a polygon stack but its polygons are open
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
        elif  isinstance(lines[0][0],int):
            self.lines  = [lines]
            self.isEmpty = False
        elif  isinstance(lines[0][0][0],int):
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
            return Line_stack([])
        return Line_stack(inter_layers(self.lines,other.polygons , False))

    def union_with(self, other):
        pass

    def difference_with(self, other):
        if other.isEmpty:
            return Line_stack(self.lines) # same return format
        if self.isEmpty:
            return Line_stack([])
        try:
            return Line_stack(diff_layers(self.lines,other.polygons , False))
        except:
            raise RuntimeError

    def get_print_line(self):
        if not self.isEmpty:
            return pyclipper.scale_from_clipper(self.lines)
        else:
            return []
    def return_start_end_point(self):
        if self.isEmpty:
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
        self.isEmpty = False
    def offset_point(self, offset_value):
        points = []
        for each_line in self.lines:
            if len(each_line) == 1:
                points.append(each_line)

        sol = LinesOffset(points, offset_value)
        for each_line_index in range(len(sol)): 
            sol[each_line_index].append(sol[each_line_index][0])

        return sol
    def offset_line(self, offset_value):
        sol = []
        #  offset for lines only
        lines = []
        for each_line in self.lines:
            if len(each_line) != 1:
                lines.append(each_line)

        sol += LinesOffset(lines, offset_value)
        return sol
    def clean(self):
        lines = []
        for each_line in self.lines:
            if len(each_line) > 0:
                lines.append(each_line)
        self.lines = lines