from gcode_writer import *
import pyclipper
from infill_paterns import *
from clipper_operations import *
from path_planner import *
from utils import *

import numpy as np

class Outline:
    def __init__(self,island,polygons):

        self.island = island
        self.polygons = polygons
        self.boundary = self.Boundary(self, polygons[0])
        self.holes  = []
        for poly_index in range(1, len(polygons)):
            self.holes.append(self.Hole(self, polygons[poly_index]))

    class Hole():
        def __init__(self,outline, polygon):
            self.outline = outline
            self.polygon = polygon
            self.shells = []
            self.polylines = []

        def make_shells(self):
            # shell = Outline.process_shell(self.polygon,0.8)
            # if len(shell) != 0:
            #     self.shells.append(shell)
            shell = Outline.process_shell(self.polygon,0.8)
            boundary_innershell = self.outline.boundary.get_innershell()
            # self.shells.append(shell)

            # if len(boundary_innershell) != 0:
            # diff = diff_layers_as_path(shell,boundary_innershell,True )
            # if len(diff_layers_as_path(shell,boundary_innershell,True )) != 0:
            #     print("didid")
            if len(diff_layers_as_path(shell,boundary_innershell,True, False )) == 0:
                self.shells.append(shell)


        def g_print(self):
            self.polylines.append(Outline.process_polyline(self.polygon))
            for shell in self.shells:
                self.polylines.append(Outline.process_polyline(shell))
            return self.polylines

        def get_innershell(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1]
            else:
                return self.polygon

    class Boundary():
        def __init__(self,outline, polygon):
            self.outline = outline
            self.polygon = polygon
            self.shells = []
            self.polylines = []

        def make_shells(self):
            # shell = Outline.process_shell(self.polygon,-0.8)
            # if len(shell) != 0:
            #     self.shells.append(shell)
            shell = Outline.process_shell(self.polygon,-0.8)
            # self.shells.append(shell)

            intersect_existing_shell = False
            for hole in self.outline.holes:
                hole_innershell = hole.get_innershell()
                if len(hole_innershell) != 0:
                    if (len(diff_layers_as_path(hole_innershell,shell,True,False )) != 0):
                        intersect_existing_shell = True

            if not intersect_existing_shell:
                self.shells.append(shell)

        def g_print(self):
            self.polylines.append(Outline.process_polyline(self.polygon))
            for shell in self.shells:
                self.polylines.append(Outline.process_polyline(shell))
            return self.polylines

        def get_innershell(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1]
            else:
                return self.polygon


    def get_innershells(self):
        innershells = []

        innershells.append(self.boundary.get_innershell())
        for hole in self.holes:
            innershells.append(hole.get_innershell())

        return innershells

    def make_shells(self):
        self.boundary.make_shells()
        for hole in self.holes:
            hole.make_shells()




    # todo: replace with a pyclipper wrap
    @staticmethod
    def process_shell(polygon,offset):
        # clipper_polygon = pyclipper.scale_to_clipper(polygon)
        po = pyclipper.PyclipperOffset()
        po.AddPath(polygon,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        clipper_offset = pyclipper.scale_to_clipper(offset)
        # offset_poly = pyclipper.scale_from_clipper(po.Execute(clipper_offset))
        offset_poly = po.Execute(clipper_offset)
        if len(offset_poly) >0:
            return  offset_poly[0]
        else:
            return []

    @staticmethod
    def process_polyline(polygon):
        polygon = pyclipper.scale_from_clipper(polygon)
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
            skin_islands = skin.skins_as_island_stack
        else:
            skin_islands = []

        self.polylines = self.make_polyline(polygons,skin_islands, layer_index)


    def make_polyline(self,polygons,skin_islands, layer_index):

        polylines = []
        # slice_min = np.min(self.BBox)
        # slice_max = np.max(self.BBox)
        # first two layers and last two layers are set to be fully filled
        if layer_index == 1 or layer_index == 2 or layer_index == len(self.layers) - 2 or layer_index == len(self.layers)-1:
            self.pattern = pyclipper.scale_to_clipper(linear_infill(0.8,self.XorY,self.BBox))
        else: # low infill density
            self.pattern = pyclipper.scale_to_clipper(linear_infill(3,self.XorY,self.BBox))

        innerlines =[]
        if len(self.polygons[0]) == 0:
            print("fdf")
        innerlines_as_tree = inter_layers(self.pattern,self.polygons[0],False)
        for interline in innerlines_as_tree.Childs:
            innerlines.append(interline.Contour)
        # innerlines = pyclipper.scale_from_clipper(innerlines)


        for hole_index in range(1, len(self.polygons)):
            if len(self.polygons[hole_index]) != 0:
                innerlines_as_tree = diff_layers(innerlines,self.polygons[hole_index],False)
                innerlines =[]

                for interline in innerlines_as_tree.Childs:
                    innerlines.append(interline.Contour)
                # innerlines = pyclipper.scale_from_clipper(innerlines)


        for skin_index in range(len(skin_islands)):
            if  len(innerlines) != 0:
                # innerlines_as_tree = diff_layers(innerlines,pyclipper.scale_from_clipper(skin_polygons[skin_index]),False)
                innerlines_as_tree = diff_layers(innerlines,skin_islands[skin_index].Contour,False)
                innerlines =[]

                for interline in innerlines_as_tree.Childs:
                    innerlines.append(interline.Contour)
                # innerlines = pyclipper.scale_from_clipper(innerlines)

        return pyclipper.scale_from_clipper(innerlines)


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
    def __init__(self,skins_as_island_stack,layers,layer_index,BBox):
        self.layers = layers
        self.skins_as_island_stack =skins_as_island_stack
        self.BBox = BBox
        self.XorY = (layer_index+1)%2
        self.pattern = None

        self.polylines = self.make_polyline(skins_as_island_stack, layer_index)


    def make_polyline(self,skins_as_island_stack,layer_index):

        self.pattern = pyclipper.scale_to_clipper(linear_infill(0.8,self.XorY,self.BBox))
        innerlines =[]
        for island in skins_as_island_stack:
            # vizz_2d(island.Contour)
            innerlines += pyclipper.OpenPathsFromPolyTree(inter_layers(self.pattern,island.Contour,False))
        for island in skins_as_island_stack:
            for hole in island.Childs:
                innerlines = pyclipper.OpenPathsFromPolyTree(diff_layers(innerlines,hole.Contour,False))
            # if len(polygon) != 0:
            #     # innerlines += pyclipper.OpenPathsFromPolyTree(inter_layers(self.pattern,pyclipper.scale_from_clipper(polygon),False))
            #     innerlines += pyclipper.OpenPathsFromPolyTree(inter_layers(self.pattern,polygon,False))
            #     # print("gsgsgxg")
            #     # pyclipper.PolyTreeToPaths()

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
