from slicer.print_tree.Island_stack import *
from slicer.print_tree.clipper_operations import *
from slicer.commons.utils import scale_list_from_clipper, \
                                 scale_point_from_clipper, \
                                 scale_value_from_clipper, \
                                 scale_line_from_clipper


'''
Polygon stack are generally used
when a clipper operation is made on a group of polygon
'''
class PolygonStack(object):
    def __init__(self, polygons=None):
        if sys.version_info[0] == 3:
            if polygons is None:
                self.polygons = []
            elif isinstance(polygons, PolygonStack):
                self.polygons = polygons.polygons
            elif isinstance(polygons, list) and len(polygons) == 0:
                self.polygons = []
            elif isinstance(polygons[0][0], int):
                self.polygons = [polygons]
            elif isinstance(polygons[0][0][0], int):
                self.polygons = polygons
            else:
                raise TypeError
        else:
            if polygons is None:
                self.polygons = []
            elif isinstance(polygons, PolygonStack):
                self.polygons = polygons.polygons
            elif isinstance(polygons, list) and len(polygons) == 0:
                self.polygons = []
            elif isinstance(polygons[0][0], int) or \
                    isinstance(polygons[0][0], long):
                self.polygons = [polygons]
            elif isinstance(polygons[0][0][0], int) or \
                    isinstance(polygons[0][0][0], long):
                self.polygons = polygons
            else:
                raise TypeError

    def add_polygons(self, polygons):
        if sys.version_info[0] == (3):
            if isinstance(polygons[0][0][0], int):
                self.polygons += polygons
            else:
                raise TypeError
        else:
            if isinstance(polygons[0][0][0], int) or \
                    isinstance(polygons[0][0][0], long):
                self.polygons += polygons
            else:
                raise TypeError

    def add_polygon(self, polygon):
        if isinstance(polygon[0][0], int):
            self.polygons.append(polygon)
        else:
            raise TypeError

    def add_polygon_stack(self, polygon_stack):
        if isinstance(polygon_stack, PolygonStack):
            self.polygons += polygon_stack.polygons
        else:
            raise TypeError

    def split_in_islands(self):
        base = pow(10, 15)
        empty_poly = PolygonStack([[[base, base],
                                     [base+1, base],
                                     [base+1, base+1],
                                     [base, base+1]]])
        polytree = diff_layers_as_polytree(self.polygons,
                                           empty_poly.polygons,
                                           True)
        island_stack = IslandStack(polytree)
        return island_stack.get_islands()

    # def get_polygons_contours(self):
    #     contours = []
    #     for polygon  in self.polygons:
    #         contours += polygon.get_contour()
    #
    #     return contours

    def intersect_with(self, other):
        if self.is_empty() or other.is_empty():
            return PolygonStack()
        return PolygonStack(inter_layers(self.polygons, other.polygons, True))

    def union_with(self, other):
        if self.is_empty() and other.is_empty():
            return PolygonStack()
        elif self.is_empty():
            return other
        elif other.is_empty():
            return self
        else:
            return PolygonStack(union_layers(self.polygons,
                                              other.polygons,
                                              True))

    def union_self(self):
        if self.is_empty():
            return PolygonStack()
        else:
            return PolygonStack(union_itself(self.polygons, True))

    def difference_with(self, other):
        if self.is_empty():
            return PolygonStack()
        elif other.is_empty():
            return self
        else:
            return  PolygonStack(diff_layers(self.polygons,
                                              other.polygons,
                                              True))

    def offset(self, val):
        return PolygonStack(offset(self, val))

    def offset_default(self, val):
        return PolygonStack(offset_default(self, val))

    # //protoype
    def get_print_line(self):
        polylines = []
        for polygon in self.polygons:
            if len(polygon) == 0:
                break
            polygon = scale_line_from_clipper(polygon)

            polyline = []
            start_point = polygon[0]  # frist vertex of the polygon
            polyline.append(start_point)
            for point in polygon[1:]:  # the rest of the vertices
                polyline.append(point)

            ''' goes back to the start point since the polygon does not 
            repeat the start (end) vertice twice'''
            polyline.append(start_point)
            polylines.append(polyline)
        return polylines

    def is_empty(self):
        if self.polygons:
            return False
        else:
            return True

    def visualize(self, bounding_box=None):
        if bounding_box is None:
            bounding_box = self.bounding_box()
        import matplotlib.pyplot as plt
        ax = plt.axes()
        for each_polygon in self.polygons:
            for this_vertex, next_vertex in zip(each_polygon, each_polygon[1:]):
                this_vertex = scale_point_from_clipper(this_vertex)
                next_vertex = scale_point_from_clipper(next_vertex)
                plt.plot([this_vertex[0], next_vertex[0]],
                         [this_vertex[1], next_vertex[1]])
                ax.arrow(this_vertex[0],
                         this_vertex[1],
                         next_vertex[0] - this_vertex[0],
                         next_vertex[1] - this_vertex[1],
                         head_width=0.05,
                         head_length=0.05,
                         fc='k',
                         ec='k')
            last_vertex = scale_point_from_clipper(each_polygon[-1])
            first_vertex = scale_point_from_clipper(each_polygon[0])
            ax.arrow(last_vertex[0],
                     last_vertex[1],
                     first_vertex[0] - last_vertex[0],
                     first_vertex[1] - last_vertex[1],
                     head_width=0.05,
                     head_length=0.05,
                     fc='k',
                     ec='k')
        plt.show()

    def total_area(self):
        total_area = 0
        for polygon in self.polygons:
            '''
            note that area is positive if orientation is anticlockwise
            negative if orientation is clockwise,
            which means this polygon is hole
            the result here will be the remaining area of all the polygon
            '''
            total_area += pyclipper.Area(scale_line_from_clipper(polygon))
        return total_area

    def remove_small_polygons(self, small_area_threshold):
        polygons = []
        for polygon in self.polygons:
            if pyclipper.Area(polygon) > 5:
                polygons.append(polygon)
        return PolygonStack(polygons)

    def bounding_box(self):
        pc = pyclipper.Pyclipper()
        for polygon in self.polygons:
            pc.AddPath(polygon, pyclipper.PT_SUBJECT, True)
        clipper_bounding_rectangle = pc.GetBounds()
        return BoundingBox(scale_value_from_clipper(clipper_bounding_rectangle.right),
                         scale_value_from_clipper(clipper_bounding_rectangle.left),
                         scale_value_from_clipper(clipper_bounding_rectangle.top),
                         scale_value_from_clipper(clipper_bounding_rectangle.bottom))
