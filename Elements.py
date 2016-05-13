from clipper_operations import *
from path_planner import *
from utils import *
from Polygon_stack import *
from Line_stack import *
from config import *
from SingleLine import SingleLine
from Line_group import *
from Polynode import Polynode
import Island
import config
import numpy as np




class Outline:

    def __init__(self,island,polygons):
        self.island = island
        self.polygons = polygons
        self.empty = True
        if(len(polygons[0])>0):
            self.empty = False
            external_perimeter = SingleLine(polygons[0],config.line_width)

            scaled_external_perimeter = external_perimeter.offset(-config.line_width/2)
            if len(scaled_external_perimeter.polygons)> 1:
                for polygon_index in range(1, len(scaled_external_perimeter.polygons)):
                    layer = self.island.layer
                    island = Polynode(scaled_external_perimeter.polygons[polygon_index])
                    isle = Island.Island(layer.print_tree,island, layer.layers,layer.index,layer.BBox,layer)
                    layer.islands.append(isle)
                scaled_external_perimeter.polygons = scaled_external_perimeter.polygons[:1]
            if not scaled_external_perimeter.isEmpty:
                self.boundary = self.Boundary(self, SingleLine(scaled_external_perimeter.polygons[0],config.line_width) )
            else:
                self.boundary = self.Boundary(self, SingleLine([],config.line_width))

            self.holes  = []
            for poly_index in range(1, len(polygons)):
                polygon = Polygon_stack(polygons[poly_index])
                scaled_hole = Polygon_stack(offset(polygon, config.line_width/2))
                self.holes.append(self.Hole(self, SingleLine(scaled_hole.polygons[0], config.line_width)))

            self.holePolylines = Line_group("hole", config.line_width)
            self.innerHolePolylines = Line_group("inner_hole", config.line_width)
            self.BoundaryPolylines = Line_group("boundary", config.line_width)

            self.innerBoundaryPolylines = Line_group("inner_boundary", config.line_width)
            self.holeShells = Polygon_stack()
            self.boundaryShells = Polygon_stack()
            self.innerShells = Polygon_stack()

    def g_print(self):
        polylines = Line_group("outline")

        for bs in self.boundaryShells.polygons:
            self.innerBoundaryPolylines.add_chain(Outline.process_polyline(bs))

        for hole in self.holes:
            polylines.add_group(hole.g_print())
        polylines.add_group(self.boundary.g_print())
        polylines.add_group(self.innerBoundaryPolylines)
        return polylines


    def make_shells(self):
        if self.empty:
            return
        previousBoundaryShell = Polygon_stack(self.boundary.line.get_contour())
        poly_hole_stack = Polygon_stack()
        for hole in self.holes:
            poly_hole_stack.add_polygon(hole.line.get_contour())
        self.innerShells = Polygon_stack(previousBoundaryShell)
        self.innerShells.add_polygon_stack(poly_hole_stack)

        for i in range(1, config.shellSize, 1):
            #previousBoundaryShell = self.boundary.make_one_shell(i, previousBoundaryShell)
            pstack = Polygon_stack(self.boundary.line.offset(-i*config.line_width))

            #if previousBoundaryShell == None:
            #    return

            #faire une intersection
            pstackhole = Polygon_stack(offset(poly_hole_stack,i*config.line_width))

            pc = pyclipper.Pyclipper()
            if not pstack.isEmpty:
                pc.AddPaths(pstack.polygons, pyclipper.PT_SUBJECT,True)
                if not poly_hole_stack.isEmpty:
                    pc.AddPaths(pstackhole.polygons, pyclipper.PT_CLIP, True)
                shell = Polygon_stack(pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
                self.boundaryShells.add_polygon_stack(shell)
                self.innerShells = Polygon_stack(shell)

    def get_innershells(self):
        if self.empty:
            return Polygon_stack()
        return self.innerShells



    def get_inner_bounds(self):
        if self.empty:
            return Polygon_stack()
        return Polygon_stack(offset(self.innerShells,-config.line_width/2))


    def get_outterbounds(self):
        if self.empty:
            return Polygon_stack()
        return Polygon_stack(offset(self.innerShells, config.line_width / 2))



    @staticmethod
    def process_polyline(line):

        if len(line) == 0:
            return []
        polygon = pyclipper.scale_from_clipper(line)

        polyline = []
        start_point = polygon[0]  # frist vertex of the polygon
        polyline.append(start_point)
        for point in polygon[1:]:  # the rest of the vertices
            polyline.append(point)
        # goes back to the start point since the polygon does not repeat the start (end) vertice twice
        polyline.append(start_point)
        return polyline

    class Hole():
        def __init__(self,outline, line):
            self.outline = outline
            self.line = line
            self.shells = []
            self.polylines = Line_group("hole", config.line_width)
            self.innerPolylines = Line_group("inner_hole", config.line_width)

        def g_print(self):

            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))

            return self.polylines

        def g_print_inner_shell(self):

            for shell in self.shells:
                self.innerPolylines.add_chain(Outline.process_polyline(shell.get_contour()))
            return self.innerPolylines

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
            self.polylines = Line_group("boundary", config.line_width)
            self.innerPolylines = Line_group("inner_boundary", config.line_width)


        def g_print(self):
            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))

            return  self.polylines

        def g_print_inner_shell(self):
            for shell in self.shells:
                self.innerPolylines.add_chain(Outline.process_polyline(shell.get_contour()))
            return self.innerPolylines

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





