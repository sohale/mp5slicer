from pipeline_test import *
from Parts import *
from Polynode import *
from Skins import *

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
            self.polygons.append(polynode.contour)
        except:
            print("f")
        if len(polynode.childs) != 0:
            self.polygons += [poly.contour for poly in polynode.childs]
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
            boundaries = outline.get_innershells()
            self.infill = Infill(boundaries,self.skins ,self.layers, self.layer_index,self.BBox)

    def get_innershells(self):
        for outline in self.outlines:
            innershells = outline.get_innershells()
        return innershells

    def process_skins(self):
        if self.layer_index != 0 and self.layer_index != len(self.layers)-2 and self.layer_index != len(self.layers)-1:
            up_islands = self.print_tree[self.layer_index+1].islands
            down_islands = self.print_tree[self.layer_index-1].islands
            up_shells = []

            for island in up_islands:
                up_shells += island.get_innershells()
            down_shells = []
            for island in down_islands:
                down_shells += island.get_innershells()
            this_shells = self.get_innershells()
            skins = intersect_layers_PT(down_shells,this_shells,up_shells)
            if len(skins) != 0:
                self.skins = Skin(skins,self.layers, self.layer_index,self.BBox)

            # print("zfsgsg")






    def g_print(self):
        printable_parts = []
        for outline in self.outlines:
            printable_parts += outline.g_print()
        printable_parts += self.infill.g_print()
        if self.skins != None:
            printable_parts += self.skins.g_print()
        return  printable_parts


    # def make_skins(self,polygons,top_layer):
    #     pass
    #
    # def make_infill_with_skins(self,polygons,skins):
    #     infill = Infill(self.layers,polygons,self.layer_index,True,self.BBox)
    #     return infill
    #
    # def make_infill(self,polygons):
    #     infill = Infill(polygons,self.layer_index,False)
    #     return infill



        # if len(skin_polygons) != 0:
        #     # skins = self.make_skins(skin_polygons)
        #     # self.parts.append(skins)
        #     infill = self.make_infill_with_skins(polygons,skin_polygons)
        #     self.parts.append(infill)
        # else:
        #     infill = self.make_infill(polygons)
        #     self.parts.append(infill)



