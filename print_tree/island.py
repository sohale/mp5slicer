import slicer.config.config as config
from slicer.commons.utils import distance, get_center, visualise_polygon_list, does_bounding_box_intersect, scale_value_to_clipper
from slicer.print_tree.Elements import Outline
from slicer.print_tree.Line_group import *
from slicer.print_tree.Parts import Infill, Skin
from slicer.print_tree.Polygon_stack import *
from slicer.print_tree.Polynode import *
from collections import namedtuple
Island_bounding_box = namedtuple('Island_bounding_box', 'xmax xmin ymax ymin')


class Island(object):
    def __init__(self, print_tree, polynode, layers, layer_index, bounding_box, layer):
        self.layer = layer
        self.print_tree = print_tree
        self.outline = None
        self.skins = None
        self.infill = None
        self.layer_index = layer_index
        self.layers = layers
        self.bounding_box = bounding_box  # bounding box for mesh
        self.polygons = []
        try:
            self.polygons.append(polynode.Contour)

        except:
            raise RuntimeError
        try:
            self.island_bounding_box = PolygonStack(polynode.Contour).bounding_box()
        except pyclipper.ClipperException:
            self.island_bounding_box = Island_bounding_box(bounding_box.xmax,
                                                           bounding_box.xmin,
                                                           bounding_box.ymax,
                                                           bounding_box.ymin)

        if len(polynode.Childs) != 0:
            self.polygons += [poly.Contour for poly in polynode.Childs]

        # visualise_polygon_list(self.polygons, self.obb)

        self.process_outlines(self.polygons)
        self.process_shells()

    def get_platform_bound(self):
        return self.outline.get_platform_bound()

    def get_raft_base(self):
        return self.outline.get_raft_base()

    def process_outlines(self, polygons):
        self.outline = Outline(self, polygons)

    def process_shells(self):
        pass
    #     self.outline.make_shells() # make shell when initial

    def process_infill(self):

        boundaries = self.outline.get_innerbounds()
        self.infill = Infill(boundaries,
                             self.skins,
                             self.layers,
                             self.layer_index,
                             self.bounding_box)

    def get_inner_shells(self):
        innershells = self.outline.get_inner_shells()
        return innershells

    def get_innerbounds(self):
        innerbounds = self.outline.get_innerbounds()
        return innerbounds

    def get_outterbounds(self):
        outterbounds = self.outline.get_outterbounds()
        return outterbounds


    # @profile
    def prepare_skins(self):
        if self.layer_index + 1 < len(self.layers):
            up_islands = self.print_tree[self.layer_index+1].islands
        else:
            up_islands = []
            up_islands.append(
                Island(self.print_tree,
                       Polynode([]),
                       self.layers,
                       self.layer_index+1,
                       self.bounding_box,
                       self.layer))


        if self.layer_index - 1 > 0:
            down_islands = self.print_tree[self.layer_index-1].islands
        else:
            down_islands = []
            down_islands.append(
                Island(self.print_tree,
                       Polynode([]),
                       self.layers,
                       self.layer_index-1,
                       self.bounding_box,
                       self.layer))

        up_shells = PolygonStack()
        for island in up_islands:
            if does_bounding_box_intersect(self.island_bounding_box,
                                           island.island_bounding_box):
                up_shells.add_polygon_stack(island.get_inner_shells())

        down_shells = PolygonStack()
        for island in down_islands:
            if does_bounding_box_intersect(self.island_bounding_box,
                                           island.island_bounding_box):
                down_shells.add_polygon_stack(island.get_inner_shells())

        this_shells = self.get_innerbounds()

        self.downskins = this_shells.difference_with(down_shells)

        self.upskins = this_shells.difference_with(up_shells)

    # @profile
    def process_skins(self):

        top_layers_indexes_to_agregate = \
            range(self.layer_index,
                  min(self.layer_index + config.upSkinsCount, len(self.layers)))

        bottom_layers_indexes_to_agregate = \
            range(max(self.layer_index - config.downSkinsCount, 0),
                  self.layer_index+1)

        upskins = PolygonStack()
        downskins = PolygonStack()
        perimeter = self.outline.get_innerbounds()

        # for layer_index in top_layers_indexes_to_agregate:
        #     other_skins = self.print_tree[layer_index].get_upskins()
        #     upskins = upskins.union_with(other_skins)

        # for layer_index in top_layers_indexes_to_agregate:
        #     other_skins = self.print_tree[layer_index].get_downskins()
        #     downskins = downskins.union_with(other_skins)

        for layer_index in top_layers_indexes_to_agregate:
            # layer = self.print_tree[layer_index]
            other_skins = PolygonStack()
            for island in self.print_tree[layer_index].islands:
                if not island.upskins.is_empty() and \
                   does_bounding_box_intersect(island.island_bounding_box,
                                               self.island_bounding_box):
                    other_skins.add_polygon_stack(island.upskins)
            upskins = upskins.union_with(other_skins)


        for layer_index in reversed(bottom_layers_indexes_to_agregate):
            # layer = self.print_tree[layer_index]
            other_skins = PolygonStack()
            for island in self.print_tree[layer_index].islands:
                if not island.downskins.is_empty() and \
                   does_bounding_box_intersect(island.island_bounding_box,
                                               self.island_bounding_box):
                    other_skins.add_polygon_stack(island.downskins)
            downskins = downskins.union_with(other_skins)

        middle_points = []

        orientation = None
        pc = pyclipper.Pyclipper()
        if not self.downskins.is_empty():
            from math import acos
            for skin in downskins.polygons:
                skin_ps = PolygonStack(skin)
                if self.layer_index != 0:
                    pc.Clear()
                    pc.AddPath(skin, pyclipper.PT_SUBJECT)
                    skin_bounding_box = pc.GetBounds()
                    anchors = skin_ps.intersect_with(self.print_tree[self.layer_index-1].get_restricted_outline(skin_bounding_box))
                    if len(anchors.polygons) == 2:
                        for anchor in anchors.polygons:
                            pc.Clear()
                            pc.AddPath(anchor, pyclipper.PT_SUBJECT)
                            bounding_box = pc.GetBounds()
                            middle_points.append(get_center(bounding_box))
                        dx = middle_points[1][0] - middle_points[0][0]
                        d = distance(middle_points[0], middle_points[1])
                        if d > 0:
                            orientation = acos(dx/d)

        self.skins = Skin(downskins,
                          upskins,
                          self.layers,
                          self.layer_index,
                          self.island_bounding_box,
                          orientation)

        self.skins.process(PolygonStack(), perimeter)

    def g_print(self):
        printable_parts = LineGroup("island", False)
        printable_parts.add_group(self.outline.g_print())

        if self.skins is not None:
            printable_parts.add_group(self.skins.g_print())

        printable_parts.add_group(self.infill.g_print())
        return printable_parts
