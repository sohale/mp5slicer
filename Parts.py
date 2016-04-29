from gcode_writer import *
import pyclipper
from infill_paterns import *
from clipper_operations import *
from path_planner import *
from utils import *
from Polygon_stack import *
from Line_stack import *
from config import *
from Line import Line
from Line_group import *

import numpy as np

settings = PrintSettings({})

class Outline:
    def __init__(self,island,polygons):

        self.island = island
        self.polygons = polygons
        polygon = Polygon_stack(polygons[0])
        self.boundary = self.Boundary(self, Line(polygon,settings.line_width) )
        self.holes  = []
        for poly_index in range(1, len(polygons)):
            polygon = Polygon_stack(polygons[poly_index])
            self.holes.append(self.Hole(self, Line(polygon, settings.line_width)))

    class Hole():
        def __init__(self,outline, line):
            self.outline = outline
            self.line = line
            self.shells = []
            self.polylines = Line_group("hole", settings.line_width)

        def make_shells(self):

            shell = Outline.process_shell(self.line,settings.line_width)
            boundary_innershell = self.outline.boundary.get_innershell()

            if len(shell.get_outter_bound().difference_with(boundary_innershell ).polygons) == 0:
                self.shells.append(shell)


        def g_print(self):

            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))
            for shell in self.shells:
                self.polylines.add_chain(Outline.process_polyline(shell.get_contour()))
            return self.polylines

        def get_innershell(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1].get_contour()
            else:
                return self.line.get_contour()

        def get_inner_bound(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1].get_outter_bound()
            else:
                return self.line.get_outter_bound()

        def get_outter_bound(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1].get_inner_bound()
            else:
                return self.line.get_inner_bound()

    class Boundary():
        def __init__(self,outline, line):
            self.outline = outline
            self.line = line
            self.shells = []
            self.polylines = Line_group("boundary", settings.line_width)

        def make_shells(self):
            shell = Outline.process_shell(self.line,-settings.line_width)

            intersect_existing_shell = False
            for hole in self.outline.holes:
                hole_innershell = hole.get_outter_bound()
                # if len(hole_innershell) != 0:
                if (len(hole_innershell.difference_with(shell.get_inner_bound()).polygons) != 0):
                    intersect_existing_shell = True

            if not intersect_existing_shell:
                self.shells.append(shell)

        def g_print(self):
            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))
            for shell in self.shells:
                self.polylines.add_chain(Outline.process_polyline(shell.get_contour()))

            return self.polylines

        def get_innershell(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1].get_contour()
            else:
                return self.line.get_contour()

        def get_inner_bound(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1].get_inner_bound()
            else:
                return self.line.get_inner_bound()

        def get_outterbound(self):
            if len(self.shells) != 0:
                return self.shells[len(self.shells)-1].get_outter_bound()
            else:
                return self.line.get_outter_bound()


    def get_innershells(self):
        innershells = Polygon_stack()

        innershells.add_polygon_stack(self.boundary.get_innershell())
        for hole in self.holes:
            innershells.add_polygon_stack(hole.get_innershell())

        return innershells

    def get_inner_bounds(self):
        inner_bounds = Polygon_stack()

        inner_bounds.add_polygon_stack(self.boundary.get_inner_bound())
        for hole in self.holes:
            inner_bounds.add_polygon_stack(hole.get_inner_bound())

        return inner_bounds

    def get_outterbounds(self):
        outter_bounds = Polygon_stack()

        outter_bounds .add_polygon_stack(self.boundary.get_outterbound())
        for hole in self.holes:
            outter_bounds.add_polygon_stack(hole.get_outter_bound())

        return outter_bounds

    def make_shells(self):
        self.boundary.make_shells()
        for hole in self.holes:
            hole.make_shells()


    @staticmethod
    def process_shell(line,offset_val):
        contour = line.get_contour()
        offset_poly = Polygon_stack(offset(contour,offset_val))

        return  Line(offset_poly, line.width)


    @staticmethod
    def process_polyline(line):
        if len(line.polygons) == 0:
            return []
        polygon = pyclipper.scale_from_clipper(line.polygons[0])

        polyline = []
        start_point = polygon[0] # frist vertex of the polygon
        polyline.append(start_point)
        for point in polygon[1:]: # the rest of the vertices
            polyline.append(point)
        # goes back to the start point since the polygon does not repeat the start (end) vertice twice
        polyline.append(start_point)
        # print_line = Line_group(line.width)
        # print_line.add_chain(polyline)
        return polyline

    def g_print(self):
        polylines = Line_group("outline")
        for hole in self.holes:
            polylines.add_group(hole.g_print())
        polylines.add_group(self.boundary.g_print())

        return polylines


class Infill:
    def __init__(self, polygons,skin, layers,layer_index,BBox):
        self.layers =layers
        self.polygons =polygons
        self.BBox = BBox
        self.XorY = layer_index%2
        self.pattern = None
        if isinstance(skin, Skin):
            skin_islands = skin.skins_as_polygon_stack
        else:
            skin_islands = []

        self.polylines = self.make_polyline(polygons,skin_islands, layer_index)


    def make_polyline(self,polygons,skin_islands, layer_index):

        polylines = []
        # slice_min = np.min(self.BBox)
        # slice_max = np.max(self.BBox)
        # first two layers and last two layers are set to be fully filled
        if layer_index == 1 or layer_index == 2 or layer_index == len(self.layers) - 2 or layer_index == len(self.layers)-1:
             self.pattern = Line_stack(pyclipper.scale_to_clipper(linear_infill(settings.line_width,self.XorY,self.BBox)))
        else: # low infill density
             self.pattern = Line_stack(pyclipper.scale_to_clipper(linear_infill(7,self.XorY,self.BBox)))
        if layer_index != 0 and layer_index != len(self.layers)-2 and layer_index != len(self.layers)-1:

            if not skin_islands.isEmpty:
                innerlines = Line_stack(self.pattern.intersect_with(polygons))
                innerlines = innerlines.difference_with(skin_islands)
            else:
                innerlines = self.pattern.intersect_with(polygons)
        else:
            innerlines = self.pattern.intersect_with(polygons)

        # if len(self.polygons[0]) == 0:
        #     print("fdf")
        # innerlines_as_tree = inter_layers(self.pattern,self.polygons[0],False)
        # for interline in innerlines_as_tree.Childs:
        #     innerlines.append(interline.Contour)
        # # innerlines = pyclipper.scale_from_clipper(innerlines)
        #
        #
        # for hole_index in range(1, len(self.polygons)):
        #     if len(self.polygons[hole_index]) != 0:
        #         innerlines_as_tree = diff_layers(innerlines,self.polygons[hole_index],False)
        #         innerlines =[]
        #
        #         for interline in innerlines_as_tree.Childs:
        #             innerlines.append(interline.Contour)
        #         # innerlines = pyclipper.scale_from_clipper(innerlines)
        #
        #
        # for skin_index in range(len(skin_islands)):
        #     if  len(innerlines) != 0:
        #         # innerlines_as_tree = diff_layers(innerlines,pyclipper.scale_from_clipper(skin_polygons[skin_index]),False)
        #         innerlines_as_tree = diff_layers(innerlines,skin_islands[skin_index].Contour,False)
        #         innerlines =[]
        #
        #         for interline in innerlines_as_tree.Childs:
        #             innerlines.append(interline.Contour)
        #         # innerlines = pyclipper.scale_from_clipper(innerlines)
        try:
            return pyclipper.scale_from_clipper(innerlines)
        except:
            print("uheufheueh")


    def process_polyline(self,polygon):

        if len(polygon) == 0:
            return []
        polyline = []
        start_point = polygon[0] # frist vertex of the polygon
        polyline.append(start_point)
        for point in polygon[1:]: # the rest of the vertices
            polyline.append(point)
        return polyline




    def g_print(self):
        polylines = Line_group("infill", settings.line_width)
        for polyline in self.polylines:
            polylines.add_chain(self.process_polyline(polyline))
        arrange_path(polylines)
        return polylines

class Skin:
    def __init__(self,downskins, upskins,layers,layer_index,BBox):
        self.layers = layers
        self.layer_index = layer_index
        self.skins_as_polygon_stack =Polygon_stack()
        self.skins_as_polygon_stack.add_polygon_stack(downskins)
        self.skins_as_polygon_stack.add_polygon_stack(upskins)
        self.downskins = downskins
        self.upskins = upskins
        self.BBox = BBox
        self.XorY = (layer_index+1)%2
        self.pattern = None

        self.polylines = None


    def process(self, skins, perimeter):
        self.skins_as_polygon_stack.add_polygon_stack(skins)


        self.pattern = Line_stack(pyclipper.scale_to_clipper(linear_infill(settings.line_width,self.XorY,self.BBox)))
        innerlines =  Line_stack(self.pattern.intersect_with(self.skins_as_polygon_stack))
        innerlines = innerlines.intersect_with(perimeter)

        innerlines = pyclipper.scale_from_clipper(innerlines)

        self.polylines = innerlines


    def process_polyline(self,polygon):
        if len(polygon) == 0:
            return []
        polyline = []
        start_point = polygon[0] # frist vertex of the polygon
        polyline.append(start_point)
        for point in polygon[1:]: # the rest of the vertices
            polyline.append(point)
        return polyline




    def g_print(self):
        polylines = Line_group("skin", settings.line_width)
        for polyline in self.polylines:
            polylines.add_chain(self.process_polyline(polyline))
        arrange_path(polylines)
        return polylines
