from utils import *
from Parts import *
from Polynode import *
from clipper_operations import *
from Polygon_stack import *

class Island():
    def __init__(self,print_tree, polynode, layers,layer_index,BBox ):
        self.print_tree = print_tree
        self.type = None # object/support/enclosure/ raft
        self.outlines = []
        self.skins = None
        self.infill = None
        self.layer_index = layer_index
        self.layers = layers
        self.BBox = BBox
        self.polygons = []
        try:
            self.polygons.append(polynode.Contour)
        except:
            print("f")
        if len(polynode.Childs) != 0:
            self.polygons += [poly.Contour for poly in polynode.Childs]
        self.process_outlines(self.polygons)
        self.process_shells()
        # self.process_infill()

    def process_outlines(self, polygons):
        self.outlines.append(Outline(self, polygons))

    def process_shells(self):
        for outline in self.outlines:
            outline.make_shells()

    def process_infill(self):

        for outline in self.outlines:
            boundaries = Polygon_stack(outline.get_innershells())
            self.infill = Infill(boundaries,self.skins ,self.layers, self.layer_index,self.BBox)

    def get_innershells(self):
        for outline in self.outlines:
            innershells = outline.get_innershells()
        return innershells

    def process_skins(self):
        if self.layer_index != 0 and self.layer_index != len(self.layers)-2 and self.layer_index != len(self.layers)-1:
            up_islands = self.print_tree[self.layer_index+1].islands
            down_islands = self.print_tree[self.layer_index-1].islands

            up_shells = Polygon_stack()
            for island in up_islands:
                up_shells.add_polygons(island.get_innershells())

            down_shells = Polygon_stack()
            for island in down_islands:
                innershells = island.get_innershells()
                down_shells.add_polygons(innershells)

            this_shells = Polygon_stack(self.get_innershells())

            downskins = this_shells.intersect_with(down_shells)
            upskins = this_shells.intersect_with(up_shells)

            skins = Polygon_stack()
            skins.add_polygon_stack(downskins)
            skins.add_polygon_stack(upskins)
            self.skins = Skin(skins, self.layers, self.layer_index,self.BBox)
            # if self.layer_index == 8:
            #     # vizz_2d_multi(down_shells)
            #     # vizz_2d_multi(this_shells)
            #     # vizz_2d_multi(up_shells)
            # skins = intersect_layers_new(down_islands,self,up_islands)

            # if len(skins) != 0 :
            #
            #     # vizz_2d_multi(skins)
            #
            #     self.skins = Skin(skins,self.layers, self.layer_index,self.BBox)

            # print("zfsgsg")






    def g_print(self):
        printable_parts = []
        for outline in self.outlines:
            printable_parts += outline.g_print()
        printable_parts += self.infill.g_print()
        if self.skins != None:
            printable_parts += self.skins.g_print()
        return  printable_parts






