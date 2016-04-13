from gcode_writer import *
import pyclipper
from infill_paterns import *
from Skins import *
from path_planner import *

import numpy as np

class Outline:
    def __init__(self,island,polygons):

        self.island = island
        self.polygons = polygons
        self.boundary = self.Boundary(polygons[0])
        self.holes  = []
        for poly_index in range(1, len(polygons)):
            self.holes.append(self.Hole(polygons[poly_index]))

    class Hole():
        def __init__(self,polygon):
            self.polygon = polygon
            self.shells = []
            self.polylines = []

        def make_shells(self):
            self.shells.append(Outline.process_shell(self.polygon,0.8))

        def g_print(self):
            self.polylines.append(Outline.process_polyline(self.polygon))
            for shell in self.shells:
                self.polylines.append(Outline.process_polyline(shell))
            return self.polylines

    class Boundary():
        def __init__(self,polygon):
            self.polygon = polygon
            self.shells = []
            self.polylines = []

        def make_shells(self):
            self.shells.append(Outline.process_shell(self.polygon,-0.8))

        def g_print(self):
            self.polylines.append(Outline.process_polyline(self.polygon))
            for shell in self.shells:
                self.polylines.append(Outline.process_polyline(shell))
            return self.polylines



    def make_shells(self):
        for hole in self.holes:
            hole.make_shells()
        self.boundary.make_shells()

    # todo: replace with a pyclipper wrap
    @staticmethod
    def process_shell(polygon,offset):
        clipper_polygon = pyclipper.scale_to_clipper(polygon)
        po = pyclipper.PyclipperOffset()
        po.AddPath(clipper_polygon,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        clipper_offset = pyclipper.scale_to_clipper(offset)
        offset_poly = pyclipper.scale_from_clipper(po.Execute(clipper_offset))
        if len(offset_poly) >0:
            return  offset_poly[0]
        else:
            return []

    @staticmethod
    def process_polyline(polygon):
        if len(polygon) == 0:
            return []
        polyline = []
        start_point = polygon[0] # frist vertex of the polygon
        start_point = Point2D(start_point[0],start_point[1])
        polyline.append(start_point)
        for point in polygon[1:]: # the rest of the vertices
            point = Point2D(point[0],point[1])
            polyline.append(point)
        # goes back to the start point since the polygon does not repeat the start (end) vertice twice
        polyline.append(start_point)
        return polyline

    def get_innershells(self):
        innershells = []

        innershells.append(self.boundary.shells[len(self.boundary.shells)-1])
        for hole in self.holes:
            innershells.append(hole.shells[len(self.boundary.shells)-1])

        return innershells




    # @staticmethod
    # def make_polyline(polygon):
    #     polylines = []
    #     for polygon in polygons:
    #         polylines.append(self.get_polyline(polygon))
    #     return polylines

    def g_print(self):
        polylines = []
        for hole in self.holes:
            polylines += hole.g_print()
        polylines += self.boundary.g_print()

        return polylines


class Infill:
    def __init__(self, polygons,skin, layers,layer_index,BBox):
        self.layers =layers
        self.polygons =polygons
        self.BBox = BBox
        self.XorY = layer_index%2
        self.pattern = None
        if isinstance(skin, Skin):
            skin_polygon = skin.polygons
        else:
            skin_polygon = []

        self.polylines = self.make_polyline(polygons,skin_polygon, layer_index)


    def make_polyline(self,polygons,skin_polygons, layer_index):

        polylines = []
        # slice_min = np.min(self.BBox)
        # slice_max = np.max(self.BBox)
        # first two layers and last two layers are set to be fully filled
        if layer_index == 1 or layer_index == 2 or layer_index == len(self.layers) - 1 or layer_index == len(self.layers):
            self.pattern = linear_infill(0.8,self.XorY,self.BBox)
        else: # low infill density
            self.pattern = linear_infill(3,self.XorY,self.BBox)

        innerlines =[]
        if len(self.polygons[0]) == 0:
            print("fdf")
        innerlines_as_tree = inter_layers(self.pattern,self.polygons[0],False)
        for interline in innerlines_as_tree.Childs:
            innerlines.append(interline.Contour)
        innerlines = pyclipper.scale_from_clipper(innerlines)

        for hole_index in range(1, len(self.polygons)):
            if len(self.polygons[hole_index]) == 0:
                print("fdf")
            innerlines_as_tree = diff_layers(innerlines,self.polygons[hole_index],False)
            innerlines =[]

            for interline in innerlines_as_tree.Childs:
                innerlines.append(interline.Contour)
            innerlines = pyclipper.scale_from_clipper(innerlines)


        for skin_index in range(1, len(skin_polygons)):
            if len(skin_polygons[skin_index]) != 0:
                innerlines_as_tree = diff_layers(innerlines,pyclipper.scale_from_clipper(skin_polygons[skin_index]),False)
                innerlines =[]

                for interline in innerlines_as_tree.Childs:
                    innerlines.append(interline.Contour)
                innerlines = pyclipper.scale_from_clipper(innerlines)

        return innerlines


    def process_polyline(self,polygon):
        if len(polygon) == 0:
            return []
        polyline = []
        start_point = polygon[0] # frist vertex of the polygon
        start_point = Point2D(start_point[0],start_point[1])
        polyline.append(start_point)
        for point in polygon[1:]: # the rest of the vertices
            point = Point2D(point[0],point[1])
            polyline.append(point)
        return polyline




    def g_print(self):
        polylines = []
        for polyline in self.polylines:
            polylines.append(self.process_polyline(polyline))
        polylines = arrange_path(polylines)
        return polylines

class Skin:
    def __init__(self,polygons,layers,layer_index,BBox):
        self.layers = layers
        self.polygons =polygons
        self.BBox = BBox
        self.XorY = layer_index%2
        self.pattern = None

        self.polylines = self.make_polyline(polygons, layer_index)


    def make_polyline(self,polygons,layer_index):

        self.pattern = linear_infill(0.8,self.XorY,self.BBox)
        innerlines =[]
        for polygon in polygons:
            if len(polygon) != 0:
                innerlines += pyclipper.OpenPathsFromPolyTree(inter_layers(self.pattern,pyclipper.scale_from_clipper(polygon),False))
                # print("gsgsgxg")
                # pyclipper.PolyTreeToPaths()

        innerlines = pyclipper.scale_from_clipper(innerlines)

        return innerlines


    def process_polyline(self,polygon):
        if len(polygon) == 0:
            return []
        polyline = []
        start_point = polygon[0] # frist vertex of the polygon
        start_point = Point2D(start_point[0],start_point[1])
        polyline.append(start_point)
        for point in polygon[1:]: # the rest of the vertices
            point = Point2D(point[0],point[1])
            polyline.append(point)
        return polyline




    def g_print(self):
        polylines = []
        for polyline in self.polylines:
            polylines.append(self.process_polyline(polyline))
        return polylines
