from slicer.clipper_operations import *
from slicer.Polygon_stack import *
from slicer.SingleLine import SingleLine
from slicer.Line_group import *
import slicer.config as config





class Outline:

    def __init__(self,island,polygons):
        self.island = island
        self.polygons = polygons
        self.empty = True
        if(len(polygons[0])>0):
            self.empty = False

            if len(polygons) != 0:
                self.boundary = self.Boundary(self, SingleLine(polygons[0],config.line_width) )
            else:
                self.boundary = self.Boundary(self, SingleLine([],config.line_width))

            self.holes  = []
            for poly_index in range(1, len(polygons)):
                self.holes.append(self.Hole(self, SingleLine(polygons[poly_index], config.line_width)))

            self.holePolylines = Line_group("hole", config.line_width)

            self.innerBoundaryPolylines = Line_group("inner_boundary", config.line_width)
            self.skirt = Polygon_stack()
            self.holeShells = Polygon_stack()
            self.boundaryShells = Polygon_stack()
            self.innerShells = Polygon_stack()

    def get_skirt(self):
        if self.island.layer_index == 0:
            self.skirt = self.boundary.line.offset(config.line_width * 7)
        return self.skirt

    def g_print(self):
        polylines = Line_group("outline")

        for boundary_shell in reversed(self.boundaryShells.polygons):
            self.innerBoundaryPolylines.add_chain(Outline.process_polyline(boundary_shell))
        polylines.add_group(self.innerBoundaryPolylines)

        for hole in self.holes:
            polylines.add_group(hole.g_print())


        polylines.add_group(self.boundary.g_print())

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
            pstack = Polygon_stack(self.boundary.line.offset(-i*config.line_width))
            pstackhole = Polygon_stack(offset(poly_hole_stack,i*config.line_width))

            pc = pyclipper.Pyclipper()
            if not pstack.isEmpty:

                pc.AddPaths(pstack.polygons, pyclipper.PT_SUBJECT,True)
                if not poly_hole_stack.isEmpty:
                    pc.AddPaths(pstackhole.polygons, pyclipper.PT_CLIP, True)
                shell = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
                if len(shell) == 0:
                    break

                if i%2 == 0:
                    self.boundaryShells.add_polygons(shell)
                else:
                    self.boundaryShells.add_polygons(shell[::-1])

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
        bounds = Polygon_stack(self.boundary.get_outterbound())
        for hole in self.holes:
            bounds.add_polygon_stack(hole.get_outter_bound())
        return bounds

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
            self.polylines = Line_group("hole", config.line_width)

        def g_print(self):

            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))

            return self.polylines

        def get_inner_bound(self):
                return self.line.get_outter_bound()

        def get_outter_bound(self):
                return self.line.get_inner_bound()

    class Boundary():
        def __init__(self,outline, line):
            self.outline = outline
            self.line = line
            self.polylines = Line_group("boundary", config.line_width)


        def g_print(self):
            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))

            return  self.polylines

        def get_inner_bound(self):
            return self.line.get_inner_bound()

        def get_outterbound(self):
            return self.line.get_outter_bound()





