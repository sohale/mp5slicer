from slicer.Parts import Infill, Skin
from slicer.Elements import Outline
from slicer.Line_group import *
from slicer.Polynode import *
from slicer.Polygon_stack import *
import slicer.config as config
import pyclipper
from slicer.utils import get_center
from slicer.utils import distance

class Island():
    def __init__(self,print_tree, polynode, layers,layer_index,BBox, layer ):
        self.layer = layer
        self.print_tree = print_tree
        self.outline = None
        self.skins = None
        self.infill = None
        self.layer_index = layer_index
        self.layers = layers
        self.BBox = BBox
        self.polygons = []
        try:
            self.polygons.append(polynode.Contour)
        except:
            raise RuntimeError
        if len(polynode.Childs) != 0:
            self.polygons += [poly.Contour for poly in polynode.Childs]
        self.process_outlines(self.polygons)
        self.process_shells()

    def get_platform_bound(self):
        return self.outline.get_platform_bound()

    def get_raft_base(self):
        return self.outline.get_raft_base()

    def process_outlines(self, polygons):
        self.outline = Outline(self, polygons)

    def process_shells(self):

        self.outline.make_shells()

    def process_infill(self):


        boundaries = Polygon_stack(self.outline.get_inner_bounds())
        self.infill = Infill(boundaries,self.skins ,self.layers, self.layer_index,self.BBox)

    def get_innershells(self):

        innershells = self.outline.get_innershells()
        return innershells

    def get_innerbounds(self):

        innerbounds = self.outline.get_inner_bounds()
        return innerbounds

    def get_outterbounds(self):

        outterbounds = self.outline.get_outterbounds()
        return outterbounds


    # @profile
    def prepare_skins(self):

        # if self.layer_index != 0 and self.layer_index != len(self.layers)-2 and self.layer_index != len(self.layers)-1:
        if (self.layer_index +1 < len(self.layers)):
            up_islands = self.print_tree[self.layer_index+1].islands
        else:
            up_islands = []
            up_islands.append(Island(self.print_tree,Polynode([]),self.layers,self.layer_index+1,self.BBox,self.layer))

        if (self.layer_index -1 > 0):
            down_islands = self.print_tree[self.layer_index-1].islands
        else:
            down_islands  = []
            down_islands.append((Island(self.print_tree,Polynode([]),self.layers,self.layer_index-1,self.BBox,self.layer)))

        up_shells = Polygon_stack()
        for island in up_islands:
            up_shells.add_polygon_stack(island.get_innershells())

        down_shells = Polygon_stack()
        for island in down_islands:
            outterbounds = island.get_innershells()
            down_shells.add_polygon_stack(outterbounds)

        this_shells = Polygon_stack(self.get_innerbounds())


        self.downskins = this_shells.difference_with(down_shells)

        self.upskins = this_shells.difference_with(up_shells)


        # self.skins = Skin(downskins, upskins, self.layers, self.layer_index,self.BBox)




    def process_skins(self):
        # if self.layer_index != 0 and self.layer_index != len(self.layers)-2 and self.layer_index != len(self.layers)-1:
        top_layers_indexes_to_agregate = range(self.layer_index , min(self.layer_index + config.upSkinsCount, len(self.layers)))
        bottom_layers_indexes_to_agregate = range(max(self.layer_index - config.downSkinsCount, 0),self.layer_index +1)
        upskins = Polygon_stack()
        downskins = Polygon_stack()
        perimeter = self.outline.get_inner_bounds()

        for layer_index in top_layers_indexes_to_agregate:
            other_skins = self.print_tree[layer_index].get_upskins()
            upskins = upskins.union_with(other_skins)

        for layer_index in reversed(bottom_layers_indexes_to_agregate):
            other_skins = self.print_tree[layer_index].get_downskins()
            downskins = downskins.union_with(other_skins)

        middle_points = []

        orientation = None
        pc = pyclipper.Pyclipper()
        if not self.downskins.isEmpty:
            from math import acos
            for skin in downskins.polygons:
                skin = Polygon_stack(skin)
                if self.layer_index != 0:
                    anchors = skin.intersect_with(self.print_tree[self.layer_index-1].get_outline())
                    if len(anchors.polygons) == 2:
                        for anchor in anchors.polygons:
                            pc.AddPath(anchor, pyclipper.PT_SUBJECT)
                            bbox = pc.GetBounds()
                            middle_points.append(get_center(bbox))
                        dx = middle_points[1][0] - middle_points[0][0]
                        d= distance(middle_points[0], middle_points[1])
                        orientation = acos(dx/d)

        self.skins = Skin(downskins, upskins, self.layers, self.layer_index,self.BBox, orientation)
        self.skins.process(Polygon_stack(), perimeter)






    def g_print(self):
        printable_parts = Line_group("island", False)
        printable_parts.add_group(self.infill.g_print())
        printable_parts.add_group(self.outline.g_print())

        if self.skins != None:
            printable_parts.add_group(self.skins.g_print())
        return  printable_parts






