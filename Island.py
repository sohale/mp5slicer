from utils import *
from Parts import *
from Polynode import *
from clipper_operations import *
from Polygon_stack import *

class Island():
    def __init__(self,print_tree, polynode, layers,layer_index,BBox ):
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
            print("f")
        if len(polynode.Childs) != 0:
            self.polygons += [poly.Contour for poly in polynode.Childs]
        self.process_outlines(self.polygons)
        self.process_shells()
        # self.process_infill()

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

        if self.layer_index != 0 and self.layer_index != len(self.layers)-2 and self.layer_index != len(self.layers)-1:
            up_islands = self.print_tree[self.layer_index+1].islands
            down_islands = self.print_tree[self.layer_index-1].islands

            up_shells = Polygon_stack()
            for island in up_islands:
                up_shells.add_polygon_stack(island.get_innerbounds())

            down_shells = Polygon_stack()
            for island in down_islands:
                outterbounds = island.get_innerbounds()
                down_shells.add_polygon_stack(outterbounds)

            this_shells = Polygon_stack(self.get_innerbounds())

            downskins = this_shells.difference_with(down_shells)
            # vizz_2d_multi(downskins.polygons)
            upskins = this_shells.difference_with(up_shells)
            # vizz_2d_multi(upskins.polygons)

            # skins = Polygon_stack()
            # skins.add_polygon_stack(downskins)
            # skins.add_polygon_stack(upskins)
            self.skins = Skin(downskins, upskins, self.layers, self.layer_index,self.BBox)
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


    def process_skins(self):
        if self.layer_index != 0 and self.layer_index != len(self.layers)-2 and self.layer_index != len(self.layers)-1:
            top_layers_indexes_to_agregate = range(self.layer_index + 1, min(self.layer_index + 5, len(self.layers)))
            bottom_layers_indexes_to_agregate = range(max(self.layer_index - 5, 0),self.layer_index - 1 )
            skins = Polygon_stack()

            for layer_index in top_layers_indexes_to_agregate:
                other_skins = self.print_tree[layer_index].get_upskins()
                skins = skins.union_with(other_skins)

            for layer_index in bottom_layers_indexes_to_agregate:
                other_skins = self.print_tree[layer_index].get_downskins()
                skins = skins.union_with(other_skins)

            if self.skins is not None:
                self.skins.process(skins)
            elif not skins.isEmpty:
                self.skins = Skin(skins, self.layers, self.layer_index,self.BBox)
                self.skins.process(Polygon_stack())






    def g_print(self):
        printable_parts = Line_group("island")
        printable_parts.add_group(self.infill.g_print())
        printable_parts.add_group(self.outline.g_print())

        if self.skins != None:
            printable_parts.add_group(self.skins.g_print())
        return  printable_parts






