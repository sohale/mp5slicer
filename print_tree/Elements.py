import slicer.config.config as config
from slicer.print_tree.Line_group import *
from slicer.print_tree.Polygon_stack import *
from slicer.print_tree.SingleLine import SingleLine
from slicer.commons.utils import scale_line_from_clipper


class Outline(object):

    def __init__(self, island, polygons):
        self.island = island
        self.polygons = polygons
        self.empty = True
        self.ordered_shells = []
        if len(polygons[0]) > 0:
            self.empty = False

            if len(polygons) != 0:
                self.boundary = self.Boundary(
                    self, SingleLine(polygons[0], config.LINE_WIDTH))
            else:
                self.boundary = self.Boundary(
                    self, SingleLine([], config.LINE_WIDTH))

            self.holes = []
            for poly_index in range(1, len(polygons)):
                self.holes.append(self.Hole(self,
                                            SingleLine(polygons[poly_index],
                                            config.LINE_WIDTH)))

            self.hole_polylines = LineGroup("hole", True, config.LINE_WIDTH)
            self.inner_boundary_polylines = LineGroup("inner_boundary",
                                                     True,
                                                     config.LINE_WIDTH)
            self.hole_shells = PolygonStack()
            self.boundary_shells = PolygonStack()
            self.inner_shells = PolygonStack()

        self.make_shells()
        self.innerbounds = self.make_innerbounds()
        # self.innerbounds = self.get_innerbounds()

    def get_raft_base(self):
        return PolygonStack(self.boundary.line.offset(config.LINE_WIDTH * 5))

    def get_PLATFORM_BOUND(self):
        if config.PLATFORM_BOUND == "brim":
            PLATFORM_BOUND = PolygonStack(self.boundary.line.offset(config.LINE_WIDTH))

        else:
            PLATFORM_BOUND = PolygonStack(self.boundary.line.offset(config.LINE_WIDTH*5))
        return PLATFORM_BOUND

    def g_print(self):
        polylines = LineGroup("outline", False)

        if config.OUTLINE_OUTSIDE_IN:

            # printing the outer line first, optimize the z-scar
            polylines.add_group(self.boundary.g_print())

            for boundary_shell in self.boundary_shells.polygons:
                self.inner_boundary_polylines.add_chain(
                    Outline.process_polyline(boundary_shell))

            polylines.add_group(self.inner_boundary_polylines)

        else:
            for boundary_shell in reversed(self.boundary_shells.polygons):
                self.inner_boundary_polylines.add_chain(
                    Outline.process_polyline(boundary_shell))

            polylines.add_group(self.inner_boundary_polylines)

            # printing the outer line first, optimize the z-scar
            polylines.add_group(self.boundary.g_print())

        for hole in self.holes:
            polylines.add_group(hole.g_print())

        return polylines

    def make_shells(self):
        if self.empty:
            return
        previous_boundary_shell = PolygonStack(self.boundary.line.get_contour())

        poly_hole_stack = PolygonStack()
        for hole in self.holes:
            poly_hole_stack.add_polygon(hole.line.get_contour())
        self.inner_shells = PolygonStack(previous_boundary_shell)
        self.inner_shells.add_polygon_stack(poly_hole_stack)

        for i in range(1, config.SHELL_SIZE, 1):
            pstack = PolygonStack(self.boundary.line.offset(-i*config.LINE_WIDTH))
            pstackhole = PolygonStack(offset(poly_hole_stack, i*config.LINE_WIDTH))

            pc = pyclipper.Pyclipper()
            if not pstack.is_empty():

                pc.AddPaths(pstack.polygons, pyclipper.PT_SUBJECT, True)
                if not poly_hole_stack.is_empty():
                    pc.AddPaths(pstackhole.polygons, pyclipper.PT_CLIP, True)

                shell = pc.Execute(pyclipper.CT_DIFFERENCE,
                                   pyclipper.PFT_EVENODD,
                                   pyclipper.PFT_EVENODD)

                if len(shell) == 0:
                    break
                self.boundary_shells.add_polygons(shell)
                self.ordered_shells.append(shell)

                self.inner_shells = PolygonStack(shell)


    def make_innerbounds(self):
        # make innerbounds
        if self.empty:
            return PolygonStack()
        else:
            return PolygonStack(offset(self.inner_shells, -config.LINE_WIDTH/2))

    def get_inner_shells(self):
        if self.empty:
            return PolygonStack()
        return self.inner_shells

    # @profile

    def get_innerbounds(self):
        return self.innerbounds

    def get_outterbounds(self):
        if self.empty:
            return PolygonStack()
        bounds = PolygonStack(self.boundary.get_outterbound())
        for hole in self.holes:
            bounds.add_polygon_stack(hole.get_outter_bound())
        return bounds

    @staticmethod
    def process_polyline(line):

        if len(line) == 0:
            return []
        polygon = scale_line_from_clipper(line)

        polyline = []
        start_point = polygon[0]  # frist vertex of the polygon
        polyline.append(start_point)
        for point in polygon[1:]:  # the rest of the vertices
            polyline.append(point)

        '''
        goes back to the start point since the polygon does not
        repeat the start (end) vertice twice
        '''
        polyline.append(start_point)
        return polyline

    class Hole(object):
        def __init__(self, outline, line):
            self.outline = outline
            self.line = line
            self.polylines = LineGroup("hole", True, config.LINE_WIDTH)

        def g_print(self):
            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))
            return self.polylines

        def get_inner_bound(self):
                return self.line.get_outter_bound()

        def get_outter_bound(self):
                return self.line.get_inner_bound()

    class Boundary(object):
        def __init__(self, outline, line):
            self.outline = outline
            self.line = line
            self.polylines = LineGroup("boundary", True, config.LINE_WIDTH)

        def g_print(self):
            self.polylines.add_chain(Outline.process_polyline(self.line.get_contour()))
            return self.polylines

        def get_inner_bound(self):
            return self.line.get_inner_bound()

        def get_outterbound(self):
            return self.line.get_outter_bound()
