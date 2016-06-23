from slicer.clipper_operations import *
import pyclipper

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
            return []
        return inter_layers(self.lines,other.polygons , False)

    def union_with(self, other):
        pass

    def difference_with(self, other):
        if other.isEmpty:
            return self.lines # same return format
        if self.isEmpty:
            return []
        # if self.isEmpty or other.isEmpty:
            # return []
        try:
            return diff_layers(self.lines,other.polygons , False)
        except:
            raise RuntimeError

    def get_print_line(self):
        # def distance(x, y):
        #     import numpy as np 
        #     x = np.array(x)
        #     y = np.array(y)
        #     return np.linalg.norm(x-y)
        # from collections import namedtuple
        # if not self.isEmpty:
        #     data_dict = [] # integer key: {start:,end:,line:}
        #     Line_Data = namedtuple('Line_Data', 'start end line')
        #     for each_line in self.lines:
        #         data_dict.append(Line_Data(each_line[0], each_line[-1], each_line))

        #     # start at first element
        #     arranged_line = Line_stack()
        #     end = pyclipper.scale_from_clipper(data_dict.pop().end)
        #     while data_dict:
        #         shortest_distance = 999999999999999
        #         delete_index = None
        #         for i in range(len(data_dict)):
        #             print(i)
        #             start_point = pyclipper.scale_from_clipper(data_dict[i].start)
        #             if distance(start_point, end) < shortest_distance:
        #                 shortest_distance = distance(start_point, end)
        #                 delete_index = i
        #         # if delete_index == None:
        #         #     print(data_dict)
        #         #     assert len(data_dict) == 1
        #         #     delete_index = 0
                
        #         arranged_line.add_line(data_dict[delete_index].line)
        #         end = pyclipper.scale_from_clipper(data_dict[delete_index].end)
        #         print('delete ' + str(i))
        #         del data_dict[delete_index]
            # return pyclipper.scale_from_clipper(arranged_line.lines)
        # return []

        if not self.isEmpty:
            return pyclipper.scale_from_clipper(self.lines)
        else:
            return []

    def visualize(self):
        import matplotlib.pyplot as plt
        for each_polygon in self.lines:
            for this_vertex, next_vertex in zip(each_polygon, each_polygon[1:]):
                plt.plot([this_vertex[0],next_vertex[0]], [this_vertex[1],next_vertex[1]])
        plt.show()