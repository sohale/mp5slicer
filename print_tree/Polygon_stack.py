from slicer.print_tree.Island_stack import *
from slicer.print_tree.clipper_operations import *


#Polygon stack are generally used when a clipper operation is made on a group of polygon
class Polygon_stack():
    def __init__(self, polygons = None):
        self.isEmpty = True
        if sys.version_info[0] == 3:
            if polygons is None:
                self.polygons = []
            elif isinstance(polygons,Polygon_stack):
                self.polygons  = polygons.polygons
                self.isEmpty = polygons.isEmpty
            elif isinstance(polygons, list) and len(polygons) == 0:
                self.polygons  = []
            elif isinstance(polygons[0][0],int) :
                self.polygons  = [polygons]
                self.isEmpty = False
            elif isinstance(polygons[0][0][0],int) :
                self.polygons = polygons
                self.isEmpty = False
            else: raise TypeError
        else:
            if polygons is None:
                self.polygons = []
            elif isinstance(polygons,Polygon_stack):
                self.polygons  = polygons.polygons
                self.isEmpty = polygons.isEmpty
            elif isinstance(polygons, list) and len(polygons) == 0:
                self.polygons  = []
            elif isinstance(polygons[0][0],int) or isinstance(polygons[0][0],long):
                self.polygons  = [polygons]
                self.isEmpty = False
            elif isinstance(polygons[0][0][0],int) or isinstance(polygons[0][0][0],long):
                self.polygons = polygons
                self.isEmpty = False
            else: raise TypeError

    def add_polygons(self,polygons):
        if sys.version_info[0] == (3):
            if isinstance(polygons[0][0][0],int):
                self.polygons += polygons
                self.isEmpty = False
            else: raise TypeError
        else:
            if isinstance(polygons[0][0][0],int) or isinstance(polygons[0][0][0],long):
                self.polygons += polygons
                self.isEmpty = False
            else: raise TypeError

    def add_polygon(self,polygon):
        if isinstance(polygon[0][0],int):
            self.polygons.append(polygon)
            self.isEmpty = False
        else: raise TypeError

    def add_polygon_stack(self,polygon_stack):
        if isinstance(polygon_stack,Polygon_stack):
            self.polygons += polygon_stack.polygons
            if self.isEmpty:
                self.isEmpty = polygon_stack.isEmpty
        else: raise TypeError

    def split_in_islands(self):
        base = pow(10,15)
        empty_poly = Polygon_stack([[[base,base],[base+1,base],[base+1,base+1],[base,base+1]]])
        polytree = diff_layers_as_polytree(self.polygons, empty_poly.polygons, True)
        island_stack = Island_stack(polytree)
        return island_stack.get_islands()

    # def get_polygons_contours(self):
    #     contours = []
    #     for polygon  in self.polygons:
    #         contours += polygon.get_contour()
    #
    #     return contours

    def intersect_with(self, other):
        if self.isEmpty or other.isEmpty:
            return Polygon_stack()
        return Polygon_stack(inter_layers(self.polygons, other.polygons, True))

    def union_with(self, other):
        if self.isEmpty and other.isEmpty:
            return Polygon_stack()
        elif self.isEmpty:
            return other
        elif other.isEmpty:
            return self
        else:
            return Polygon_stack(union_layers(self.polygons, other.polygons, True))

    def union_self(self):
        if self.isEmpty:
            return Polygon_stack()
        else:
            return Polygon_stack(union_itself(self.polygons, True))

    def difference_with(self, other):
        if self.isEmpty :
            return Polygon_stack()

        if other.isEmpty:
            return self
        return  Polygon_stack(diff_layers(self.polygons, other.polygons, True))

    def offset(self, val):
        return Polygon_stack(offset(self,val))

    # //protoype
    def get_print_line(self):
        polylines = []
        for polygon in self.polygons:
            if len(polygon) == 0:
                break
            polygon = pyclipper.scale_from_clipper(polygon)

            polyline = []
            start_point = polygon[0]  # frist vertex of the polygon
            polyline.append(start_point)
            for point in polygon[1:]:  # the rest of the vertices
                polyline.append(point)
            # goes back to the start point since the polygon does not repeat the start (end) vertice twice
            polyline.append(start_point)
            polylines.append(polyline)
        return polylines
    def is_empty(self):
        return self.isEmpty

    def visualize(self, bbox):
        import matplotlib.pyplot as plt
        ax = plt.axes()
        for each_polygon in self.polygons:
            for this_vertex, next_vertex in zip(each_polygon, each_polygon[1:]):
                this_vertex = pyclipper.scale_from_clipper(this_vertex)
                next_vertex = pyclipper.scale_from_clipper(next_vertex)
                plt.plot([this_vertex[0], next_vertex[0]],[this_vertex[1], next_vertex[1]])
                ax.arrow(this_vertex[0], 
                            this_vertex[1], 
                            next_vertex[0] - this_vertex[0], 
                            next_vertex[1] - this_vertex[1], head_width=0.05, head_length=0.05, fc='k', ec='k')
            last_vertex = pyclipper.scale_from_clipper(each_polygon[-1])
            first_vertex = pyclipper.scale_from_clipper(each_polygon[0])
            ax.arrow(last_vertex[0], 
                        last_vertex[1], 
                        first_vertex[0] - last_vertex[0], 
                        first_vertex[1] - last_vertex[1], head_width=0.05, head_length=0.05, fc='k', ec='k')
        plt.show()

    def total_area(self):
        total_area = 0
        for polygon in self.polygons:
            # note that area is positive if orientation is anticlockwise
            # negative if orientation is clockwise, which means this polygon is hole
            # the result here will be the remaining area of all the polygon
            total_area += pyclipper.Area(pyclipper.scale_from_clipper(polygon))
        
        return total_area


    def bounding_box(self):
        pc = pyclipper.Pyclipper()
        for polygon in self.polygons:
            pc.AddPath(polygon,pyclipper.PT_SUBJECT, True)
        clipper_bounding_rectangle = pc.GetBounds()
        return Bounding_box(pyclipper.scale_from_clipper(clipper_bounding_rectangle.right),
                         pyclipper.scale_from_clipper(clipper_bounding_rectangle.left),
                         pyclipper.scale_from_clipper(clipper_bounding_rectangle.top),
                         pyclipper.scale_from_clipper(clipper_bounding_rectangle.bottom))