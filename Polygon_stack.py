from clipper_operations import *
from Island_stack import *

#Polygon stack are generally used when a clipper operation is made on a group of polygon
class Polygon_stack():
    def __init__(self, polygons = None):
        self.isEmpty = True
        if polygons is None:
            self.polygons = []
        elif isinstance(polygons,Polygon_stack):
            self.polygons  = polygons.polygons
            self.isEmpty = polygons.isEmpty
        elif isinstance(polygons, list) and len(polygons) == 0:
            self.polygons  = []
        elif isinstance(polygons[0][0],long) or isinstance(polygons[0][0],int):
            self.polygons  = [polygons]
            self.isEmpty = False
        elif isinstance(polygons[0][0][0],long) or isinstance(polygons[0][0][0],int):
            self.polygons = polygons
            self.isEmpty = False
        else: raise TypeError

    def add_polygons(self,polygons):
        if isinstance(polygons[0][0][0],long):
            self.polygons += polygons
            self.isEmpty = False
        else: raise TypeError

    def add_polygon(self,polygon):
        if isinstance(polygon[0][0],long):
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

    def difference_with(self, other):
        if self.isEmpty or other.isEmpty:
            return Polygon_stack()
        return  Polygon_stack(diff_layers(self.polygons, other.polygons, True))