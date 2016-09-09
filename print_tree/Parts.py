import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

from slicer.print_tree.infill_paterns import *
from slicer.print_tree.Line_stack import *

from slicer.print_tree.Line_group import *
import slicer.config.config as config

from slicer.commons.utils import scale_list_to_clipper, scale_value_from_clipper, scale_list_from_clipper


#
# class Outline:
#     def __init__(self,island,polygons):
#         self.island = island
#         self.polygons = polygons
#         external_perimeter = Polygon_stack(polygons[0])
#
#         scaled_external_perimeter = Polygon_stack(offset(external_perimeter, -config.line_width/2))
#         if len(scaled_external_perimeter.polygons)> 1:
#             for polygon_index in range(1, len(scaled_external_perimeter.polygons)):
#                 layer = self.island.layer
#                 island = Polynode(scaled_external_perimeter.polygons[polygon_index])
#                 isle = Island.Island(layer.print_tree,island, layer.layers,layer.index,layer.BBox,layer)
#                 layer.islands.append(isle)
#             scaled_external_perimeter.polygons = scaled_external_perimeter.polygons[:1]
#         self.boundary = self.Boundary(self, Line(scaled_external_perimeter,config.line_width) )
#         self.holes  = []
#         for poly_index in range(1, len(polygons)):
#             polygon = Polygon_stack(polygons[poly_index])
#             scaled_hole = Polygon_stack(offset(polygon, config.line_width/2))
#             self.holes.append(self.Hole(self, Line(scaled_hole, config.line_width)))
#
#     class Hole():
#         def __init__(self,outline, line):
#             self.outline = outline
#             self.line = line
#             self.shells = []
#             self.polylines = Line_group("hole", config.line_width)
#             self.innerPolylines = Line_group("inner_hole", config.line_width)
#
#         def make_one_shell(self,index):
#             shell = Outline.process_shell(self.line, index * config.line_width)
#             boundary_innershell = self.outline.boundary.get_innershell()
#
#             if len(shell.get_outter_bound().difference_with(boundary_innershell).polygons) == 0:
#                 self.shells.append(shell)
#
#         # def make_shells(self):
#         #     for i in range(1,settings.shellSize,1):
#         #         shell = Outline.process_shell(self.line,i*settings.line_width)
#         #         boundary_innershell = self.outline.boundary.get_innershell()
#         #
#         #         if len(shell.get_outter_bound().difference_with(boundary_innershell ).polygons) == 0:
#         #             self.shells.append(shell)
#
#
#         def g_print(self):
#
#             self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))
#
#             return self.polylines
#
#         def g_print_inner_shell(self):
#
#             for shell in self.shells:
#                 self.innerPolylines.add_chain(Outline.process_polyline(shell.get_contour()))
#             return self.innerPolylines
#
#         def get_innershell(self):
#             if len(self.shells) != 0:
#                 return self.shells[len(self.shells)-1].get_contour()
#             else:
#                 return self.line.get_contour()
#
#         def get_inner_bound(self):
#             if len(self.shells) != 0:
#                 return self.shells[len(self.shells)-1].get_outter_bound()
#             else:
#                 return self.line.get_outter_bound()
#
#         def get_outter_bound(self):
#             if len(self.shells) != 0:
#                 return self.shells[len(self.shells)-1].get_inner_bound()
#             else:
#                 return self.line.get_inner_bound()
#
#     class Boundary():
#         def __init__(self,outline, line):
#             self.outline = outline
#
#             self.line = line
#             self.shells = []
#             self.polylines = Line_group("boundary", config.line_width)
#             self.innerPolylines = Line_group("inner_boundary", config.line_width)
#
#         def make_one_shell(self,index,previousShell):
#             shell = Outline.process_shell(self.line, -index * config.line_width)
#
#             intersect_existing_shell = False
#             for hole in self.outline.holes:
#                 hole_innershell = hole.get_outter_bound()
#                 # if len(hole_innershell) != 0:
#                 if (len(hole_innershell.difference_with(shell.get_inner_bound()).polygons) != 0):
#                     intersect_existing_shell = True
#
#             if (not intersect_existing_shell and len(
#                     previousShell.get_outter_bound().difference_with(shell.get_inner_bound()).polygons) != 0):
#                 self.shells.append(shell)
#                 return shell
#             return None
#
#         # def make_shells(self):
#         #     previousShell = self.line
#         #     for i in range(1,settings.shellSize,1):
#         #         shell = Outline.process_shell(self.line,-i*settings.line_width)
#         #
#         #         intersect_existing_shell = False
#         #         for hole in self.outline.holes:
#         #             hole_innershell = hole.get_outter_bound()
#         #             # if len(hole_innershell) != 0:
#         #             if (len(hole_innershell.difference_with(shell.get_inner_bound()).polygons) != 0):
#         #                 intersect_existing_shell = True
#         #
#         #         if (not intersect_existing_shell and len(previousShell.get_outter_bound().difference_with(shell.get_inner_bound()).polygons) != 0):
#         #             self.shells.append(shell)
#         #             previousShell = shell
#
#
#         def g_print(self):
#             self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))
#
#             return  self.polylines
#
#         def g_print_inner_shell(self):
#             for shell in self.shells:
#                 self.innerPolylines.add_chain(Outline.process_polyline(shell.get_contour()))
#             return self.innerPolylines
#
#         def get_innershell(self):
#             if len(self.shells) != 0:
#                 return self.shells[len(self.shells)-1].get_contour()
#             else:
#                 return self.line.get_contour()
#
#         def get_inner_bound(self):
#             if len(self.shells) != 0:
#                 return self.shells[len(self.shells)-1].get_inner_bound()
#             else:
#                 return self.line.get_inner_bound()
#
#         def get_outterbound(self):
#             if len(self.shells) != 0:
#                 return self.shells[len(self.shells)-1].get_outter_bound()
#             else:
#                 return self.line.get_outter_bound()
#
#
#     def get_innershells(self):
#         innershells = Polygon_stack()
#
#         innershells.add_polygon_stack(self.boundary.get_innershell())
#         for hole in self.holes:
#             innershells.add_polygon_stack(hole.get_innershell())
#
#         return innershells
#
#     def get_innerbounds(self):
#         inner_bounds = Polygon_stack()
#
#         inner_bounds.add_polygon_stack(self.boundary.get_inner_bound())
#         for hole in self.holes:
#             inner_bounds.add_polygon_stack(hole.get_inner_bound())
#
#         return inner_bounds
#
#     def get_outterbounds(self):
#         outter_bounds = Polygon_stack()
#
#         outter_bounds .add_polygon_stack(self.boundary.get_outterbound())
#         for hole in self.holes:
#             outter_bounds.add_polygon_stack(hole.get_outter_bound())
#
#         return outter_bounds
#
#     def make_shells(self):
#         previousBoundaryShell = self.boundary.line
#         for i in range(1, config.shellSize, 1):
#             previousBoundaryShell = self.boundary.make_one_shell(i,previousBoundaryShell)
#             if previousBoundaryShell == None:
#                 return
#             for hole in self.holes:
#                 hole.make_one_shell(i)
#
#
#     @staticmethod
#     def process_shell(line,offset_val):
#         contour = line.get_contour()
#         offset_poly = Polygon_stack(offset(contour,offset_val))
#
#         return  Line(offset_poly, line.width)
#
#
#     @staticmethod
#     def process_polyline(line):
#         if len(line.polygons) == 0:
#             return []
#         polygon = pyclipper.scale_from_clipper(line.polygons[0])
#
#         polyline = []
#         start_point = polygon[0] # frist vertex of the polygon
#         polyline.append(start_point)
#         for point in polygon[1:]: # the rest of the vertices
#             polyline.append(point)
#         # goes back to the start point since the polygon does not repeat the start (end) vertice twice
#         polyline.append(start_point)
#         # print_line = Line_group(line.width)
#         # print_line.add_chain(polyline)
#         return polyline
#
#     def g_print(self):
#         polylines = Line_group("outline")
#         for hole in self.holes:
#             polylines.add_group(hole.g_print_inner_shell())
#             polylines.add_group(hole.g_print())
#         polylines.add_group(self.boundary.g_print_inner_shell())
#         polylines.add_group(self.boundary.g_print())
#
#         return polylines


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
            skin_islands = Polygon_stack()
        self.startPoint = None
        self.endPoint = None
        self.polylines = self.make_polyline(polygons,skin_islands, layer_index)


    def make_polyline(self,polygons,skin_islands, layer_index):

        teta = 45 if self.XorY else 135
        # scale test
        # self.pattern = Line_stack(pyclipper.scale_to_clipper(linear_infill2(5,teta,self.BBox)))
        self.pattern = Line_stack(scale_list_to_clipper(linear_infill2(5,teta,self.BBox)))


        if not skin_islands.is_empty():
            innerlines = self.pattern.intersect_with(polygons)
            innerlines = innerlines.difference_with(skin_islands)
        else:
            innerlines = self.pattern.intersect_with(polygons)
            self.startPoint, self.endPoint = innerlines.return_start_end_point()
        # if len(self.polygons[0]) == 0:
        #     raise StandardError
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
        return innerlines.get_print_line()
        # try:
        #     return pyclipper.scale_from_clipper(innerlines)
        # except:
        #     raise RuntimeError


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
        polylines = Line_group("infill", True, config.line_width)
        for polyline in self.polylines:
            polylines.add_chain(self.process_polyline(polyline))
        return polylines

class Skin:
    def __init__(self,downskins, upskins,layers,layer_index, island_bbox, orientation = None):
        self.layers = layers
        self.layer_index = layer_index
        downskins = Polygon_stack(offset(downskins,1))
        upskins = Polygon_stack(offset(upskins, 1))
        self.skins_as_polygon_stack = Polygon_stack()
        self.skins_as_polygon_stack = self.skins_as_polygon_stack.union_with(downskins)
        self.skins_as_polygon_stack = self.skins_as_polygon_stack.union_with(upskins)
        self.downskins = downskins
        self.upskins = upskins
        self.island_bbox = island_bbox

        self.XorY = (layer_index+1)%2
        self.pattern = None
        self.startPoint = None
        self.endPoint = None
        self.orientation = orientation

        self.polylines = None
        self.islands = self.detect_islands()

    def detect_islands(self):
        po = pyclipper.PyclipperOffset()
        po.MiterLimit = 2
        base = 1#pow(10, 15)
        empty_poly = Polygon_stack([[[base, base], [base + 1, base], [base + 1, base + 1], [base, base + 1]]])
        if self.skins_as_polygon_stack.polygons != []:
            polys = pyclipper.PolyTreeToPaths(diff_layers_as_polytree(self.skins_as_polygon_stack.polygons, empty_poly.polygons, True))
            po.AddPaths(polys, pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
            islandStack = Island_stack(po.Execute2(scale_value_to_clipper(-config.line_width/2)))
            return islandStack.get_islands()
        else:
            return []

    # def process(self, skins, perimeter):
    #     self.skins_as_polygon_stack = self.skins_as_polygon_stack.union_with(skins)
    #     skin_bbox = self.skins_as_polygon_stack.bounding_box()
    #     # self.skins_as_polygon_stack.visualize(self.island_bbox)

    #     teta = 45 if self.XorY else 135
    #     if self.orientation is not None:
    #         teta = self.orientation

    #     # self.pattern = Line_stack()
    #     # for polygon in self.skins_as_polygon_stack.polygons:
    #     #     # two things are done in the following if
    #     #     # 1. area possitive means it's not hole 
    #     #     # 2. and check it is not a very small area
    #     #     if pyclipper.Orientation(polygon): # area possitive means it's not hole and if it's not a very small area
    #     #         skin_bbox = bbox_for_single_polygon(polygon)
    #     #         pattern = Line_stack(scale_list_to_clipper(linear_infill2(config.line_width,teta,skin_bbox)))
    #     #         pattern = pattern.intersect_with(Polygon_stack(polygon))
    #     #         self.pattern = self.pattern.combine(pattern)

    #     # scale test
    #     # self.pattern = Line_stack(pyclipper.scale_to_clipper(linear_infill2(config.line_width,teta,self.BBox)))
    #     if self.skins_as_polygon_stack.total_area() > 0:
    #         self.pattern = Line_stack(scale_list_to_clipper(linear_infill2(config.line_width,teta,skin_bbox)))

    #         innerlines =  Line_stack(self.pattern.intersect_with(self.skins_as_polygon_stack))
    #         innerlines = innerlines.intersect_with(perimeter)
    #     else:
    #         innerlines = Line_stack()

    #     self.polylines = innerlines.get_print_line()
    #     self.startPoint, self.endPoint = innerlines.return_start_end_point()


    def process(self, skins, perimeter):
        self.skins_as_polygon_stack = self.skins_as_polygon_stack.union_with(skins)
        skin_bbox = self.skins_as_polygon_stack.bounding_box()
        # self.skins_as_polygon_stack.visualize(self.island_bbox)

        teta = 45 if self.XorY else 135
        if self.orientation is not None:
            teta = self.orientation

        self.pattern = Line_stack()
        for polygon in self.islands:
            # two things are done in the following if
            # 1. area possitive means it's not hole 
            # 2. and check it is not a very small area
            # if pyclipper.Orientation(polygon): # area possitive means it's not hole and if it's not a very small area
            if isinstance(polygon, pyclipper.PyPolyNode):
                polygon = polygon.Contour
            else:
                pass

            if pyclipper.Area(scale_line_from_clipper(polygon))>3:

                skin_bbox = bbox_for_single_polygon(polygon)
                pattern = Line_stack(scale_list_to_clipper(linear_infill2(config.line_width,teta,skin_bbox)))
                pattern = pattern.intersect_with(Polygon_stack(polygon))
                self.pattern = self.pattern.combine(pattern)
            else:
                self.pattern = Line_stack()

        # scale test
        # self.pattern = Line_stack(pyclipper.scale_to_clipper(linear_infill2(config.line_width,teta,self.BBox)))
        # if self.skins_as_polygon_stack.total_area() > 0:
        #     self.pattern = Line_stack(scale_list_to_clipper(linear_infill2(config.line_width,teta,skin_bbox)))

        #     innerlines =  Line_stack(self.pattern.intersect_with(self.skins_as_polygon_stack))
        #     innerlines = innerlines.intersect_with(perimeter)
        # else:
        #     innerlines = Line_stack()

        self.pattern  = self.pattern.intersect_with(perimeter)
        self.polylines = self.pattern.get_print_line()
        # self.startPoint, self.endPoint = self.pattern.return_start_end_point()



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
        polylines = Line_group("skin", True, config.line_width)
        if self.polylines != None:
            for polyline in self.polylines:
                polylines.add_chain(self.process_polyline(polyline))
        else:
            pass
        return polylines

class Support_line:
    def __init__(self):
        pass