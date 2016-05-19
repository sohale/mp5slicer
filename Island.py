from utils import *
from Parts import Infill, Skin
from Elements import Outline
from Line_group import *
from Polynode import *
from clipper_operations import *
from Polygon_stack import *

class Island():
    def __init__(self,print_tree, polynode, layers,layer_index,BBox, layer ):
        self.layer = layer
        self.print_tree = print_tree
        self.type = None # object/support/enclosure/ raft
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
            raise StandardError
        if len(polynode.Childs) != 0:
            self.polygons += [poly.Contour for poly in polynode.Childs]
        self.process_outlines(self.polygons)
        self.process_shells()
        # self.process_infill()

    def get_skirt(self):
        return self.outline.get_skirt()

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
            up_shells.add_polygon_stack(island.get_outterbounds())

        down_shells = Polygon_stack()
        for island in down_islands:
            outterbounds = island.get_outterbounds()
            down_shells.add_polygon_stack(outterbounds)

        this_shells = Polygon_stack(self.get_innerbounds())

        downskins = this_shells.difference_with(down_shells)

        upskins = this_shells.difference_with(up_shells)

        self.skins = Skin(downskins, upskins, self.layers, self.layer_index,self.BBox)



    def process_skins(self):
        # if self.layer_index != 0 and self.layer_index != len(self.layers)-2 and self.layer_index != len(self.layers)-1:
        top_layers_indexes_to_agregate = range(self.layer_index + 1, min(self.layer_index + 4, len(self.layers)))
        bottom_layers_indexes_to_agregate = range(max(self.layer_index - 2, 0),self.layer_index - 1, -1 )
        skins = Polygon_stack()
        perimeter = self.outline.get_inner_bounds()

        for layer_index in top_layers_indexes_to_agregate:
            other_skins = self.print_tree[layer_index].get_upskins()
            skins = skins.union_with(other_skins)

        for layer_index in bottom_layers_indexes_to_agregate:
            other_skins = self.print_tree[layer_index].get_downskins()
            skins = skins.union_with(other_skins)

        if self.skins is not None:
            self.skins.process(skins, perimeter)
        elif not skins.isEmpty:
            self.skins = Skin(skins, self.layers, self.layer_index,self.BBox)
            self.skins.process(Polygon_stack(), perimeter)






    def g_print(self):
        printable_parts = Line_group("island")
        printable_parts.add_group(self.infill.g_print())
        printable_parts.add_group(self.outline.g_print())

        if self.skins != None:
            printable_parts.add_group(self.skins.g_print())
        return  printable_parts






