import slicer.config.config as config
from slicer.commons.utils import overlap, does_bounding_box_intersect, scale_value_to_clipper
from slicer.print_tree.Line_group import *
from slicer.print_tree.Line_stack import *
from slicer.print_tree.island import Island
import numpy as np
from slicer.commons.utils import scale_list_to_clipper, scale_line_to_clipper
from slicer.print_tree.infill_paterns import linear_infill2

class Layer(object):

    # layers are only passed as a reference to get an acces for skin processing
    def __init__(self,
                 print_tree,
                 layers,
                 index,
                 bounding_box,
                 support_polylines=[]):

        self.print_tree = print_tree
        self.layers = layers
        self.islands = []
        self.index = index
        self.bounding_box = bounding_box
        if self.index == 0 and config.RAFT is True:
            config.LINE_WIDTH = 0.35
        self.process_islands()

        # self.support_line_stack = support_polylines[0]
        # self.support_polylines = \
        #     self.support_polygon_difference_with_outline(support_polylines)
        config.reset()

        # support
        self.support_offset_value = \
            config.LAYER_THICKNESS*np.tan(np.radians(config.SUPPORT_OVERHANG_ANGLE))

        self.support_boundary_ps = PolygonStack()

    def get_raft_base(self):
        raft_base = PolygonStack()
        for island in self.islands:
            raft_base = raft_base.union_with(island.get_raft_base())
        return raft_base

    def G_print(self):
        if self.index == 0 and config.RAFT is True:
            polylines = LineGroup("contact_layer", False)

        else:
            polylines = LineGroup("layer", False)

        if config.USE_SUPPORT:
            self.support_polylines = self.support_polygon_difference_with_outline()

        if self.index == 0 and \
                (config.PLATFORM_BOUND == "brim" or \
                 config.PLATFORM_BOUND == "skirts"):

            skirtPolylines = LineGroup("skirt", True, config.LINE_WIDTH)
            skirts = PolygonStack()
            for island in self.islands:
                skirts = skirts.union_with(island.get_PLATFORM_BOUND())
            if config.PLATFORM_BOUND == "skirts" and \
                    not self.support_boundary_ps.is_empty():
                skirts = skirts.union_with(self.support_boundary_ps.offset(config.LINE_WIDTH*3))
                # self.support_open_path.difference_with(skirts)
                # pass
            elif config.PLATFORM_BOUND == "brim" and \
                    not self.support_boundary_ps.is_empty():
                skirts = skirts.union_with(self.support_boundary_ps.offset(0))
                # self.support_open_path.difference_with(skirts)
                # pass

            else:
                pass
                # raise NotImplementedError

            skirts_all = [skirts]
            for count in range(config.PLATFORM_BOUND_COUNT):
                skirts = skirts.offset(config.LINE_WIDTH)
                skirts_all.append(skirts)
            # self.support_open_path = self.support_open_path.difference_with(skirts)
            
            for skirts in skirts_all[::-1]:  # reverse order from outside to inside
                skirtPolylines.add_chains(skirts.get_print_line())
            polylines.add_group(skirtPolylines)

        for island in self.islands:
            polylines.add_group(island.g_print())

        support_line_group = LineGroup('support', True, config.LINE_WIDTH)

        if config.USE_SUPPORT:
            for polyline in self.support_polylines:
                support_line_group.add_chain(polyline)
            polylines.add_group(support_line_group)

        return polylines

    def process_shells(self):
        for island in self.islands:
            island.process_shells()

    def process_skins(self):
        if self.index == 0 and config.RAFT is True:
            config.LINE_WIDTH = 0.35
        for island in self.islands:
            island.process_skins()
        config.reset()

    def prepare_skins(self):
        if self.index == 0 and config.RAFT is True:
            config.LINE_WIDTH = 0.35
        for island in self.islands:
            island.prepare_skins()
        config.reset()

    def prepare_support(self):

        this_layer_index = self.index
        if self.index == 0:
            one_below_layer_index = 0
        else:
            one_below_layer_index = self.index - 1

        this_layer = PolygonStack(self.layers[this_layer_index])
        one_last_layer = PolygonStack(self.layers[one_below_layer_index])
        offseted_one_last_ps = one_last_layer.offset(self.support_offset_value)

        this_layer_support_required_ps = \
            this_layer.difference_with(offseted_one_last_ps)

        this_layer_support_required_ps = \
            this_layer_support_required_ps.offset(config.SUPPORT_AREA_ENLARGE_VALUE) # think about the number
            
        self.this_layer_support_required_ps = this_layer_support_required_ps

    def process_support(self):
        this_layer_index = self.index
        if self.index == 0:
            one_below_layer_index = 0
        else:
            one_below_layer_index = self.index - 1

        if self.index == len(self.layers) - 1:
            support_required_ps = PolygonStack(self.layers[this_layer_index])
            self.support_required_ps = PolygonStack()
        else:
            support_required_ps = \
                self.support_required_ps.difference_with(PolygonStack(self.layers[this_layer_index]))

            support_required_ps = \
                support_required_ps.union_with(self.this_layer_support_required_ps)

        if config.DOES_REMOVE_SMALL_AREA:
            # clean small area
            support_required_ps = \
                support_required_ps.remove_small_polygons(config.SMALL_AREA)

        return support_required_ps  # this is for one last layer


    def support_polygon_difference_with_outline(self):

        outline = self.get_outline()
        offseted_outline = outline.offset(config.SUPPORT_HORIZONTAL_OFFSET_FROM_PARTS)

        polylines = []

        # polygons

        innerlines_whole_bounding_box = \
            LineStack(scale_list_to_clipper(linear_infill2(config.SUPPORT_SAMPLING_DISTANCE,
                                                            config.SUPPORT_LINE_ANGLE,
                                                            self.bounding_box)))

        innerlines = \
            innerlines_whole_bounding_box.intersect_with(self.support_required_ps)

        assert config.BED_SUPPORT_STRENGTHEN_LAYER_NUMBER >= 1
        if self.index in range(config.BED_SUPPORT_STRENGTHEN_LAYER_NUMBER):
            offseted_line_polygon_stack = PolygonStack()
            for i in reversed(range(config.BED_SUPPORT_STRENGTHEN_OFFSET_NUMBER)):

                offseted_line_polygon_stack.add_polygon_stack(
                    innerlines.offset_line(config.LINE_WIDTH*(i+1)))

            solution_polygon_ps = offseted_line_polygon_stack.difference_with(
                offseted_outline)

            self.support_boundary_ps = solution_polygon_ps
            polylines += solution_polygon_ps.get_print_line()

        solution_open_path_ls = innerlines.difference_with(offseted_outline)
        polylines += solution_open_path_ls.get_print_line()


        return polylines

    # def get_skins(self):
    #     skins = PolygonStack()
    #     for island in self.islands:
    #         if island.skins is not None:
    #             skins.add_polygon_stack(island.skins.skins_as_polygon_stack)
    #     return skins

    def get_downskins(self):
        skins = PolygonStack()
        for island in self.islands:
            if not island.downskins.is_empty():
                skins.add_polygon_stack(island.downskins)
        return skins

    def get_upskins(self):
        skins = PolygonStack()
        for island in self.islands:
            if not island.upskins.is_empty():
                skins.add_polygon_stack(island.upskins)
        return skins

    def process_infill(self):
        if self.index == 0 and config.RAFT is True:
            config.LINE_WIDTH = 0.35
        for island in self.islands:
            island.process_infill()
        config.reset()


    def poly1_in_poly2(self, poly1, poly2):
        point = poly1[0]
        if pyclipper.PointInPolygon(point, poly2):
            return True
        else:
            return False

    def detect_islands(self):
        po = pyclipper.PyclipperOffset()
        po.MiterLimit = 2
        base = 1#pow(10, 15)
        empty_poly = PolygonStack([[[base, base],
                                     [base + 1, base],
                                     [base + 1, base + 1],
                                     [base, base + 1]]])

        polys = pyclipper.PolyTreeToPaths(
            diff_layers_as_polytree(self.layers[self.index],
                                    empty_poly.polygons,
                                    True))

        po.AddPaths(polys, pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)

        islandStack = IslandStack(
            po.Execute2(scale_value_to_clipper(-config.LINE_WIDTH/2)))

        return  islandStack.get_islands()

    def process_islands(self):
        if len(self.layers[self.index]) != 0:
            islands = self.detect_islands()
            for island in islands:
                # pc = pyclipper.Pyclipper()
                isle = Island(self.print_tree,
                              island,
                              self.layers,
                              self.index,
                              self.bounding_box,
                              self)

                self.islands.append(isle)

    def get_outline(self):
        ps = PolygonStack()
        for island in self.islands:
            ps.add_polygons(island.get_outterbounds().polygons)
        return ps.union_self()

    def get_restricted_outline(self, bounding_box):
        ps = PolygonStack()
        for island in self.islands:
            if overlap(island.island_bounding_box, bounding_box):
                ps.add_polygons(island.get_outterbounds().polygons)
        return ps.union_self()
