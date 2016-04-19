from clipper_operations import *
from Island_stack import *

#Polygon stack are generally used when a clipper operation is made on a group of polygon
class Polygon_stack():
    def __init__(self, polygons = None):
        if polygons is None:
            self.polygons = []
        else:
            self.polygons = polygons

    def add_polygons(self,polygons):
        self.polygons += polygons

    def add_polygon(self,polygon):
        self.polygons.append(polygon)

    def add_polygon_stack(self,polygon_stack):
        self.polygons += polygon_stack.polygons

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
        return Polygon_stack(inter_layers(self.polygons, other.polygons, True))

    def union_with(self, other):
        pass

    def difference_with(self, other):
        return  Polygon_stack(diff_layers(self.polygons, other.polygons, True))