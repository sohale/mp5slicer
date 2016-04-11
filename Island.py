from pipeline_test import *
from Parts import *
from Polynode import *
from Skins import *

class Island():
    def __init__(self,print_tree, polynode, layers,layer_index,BBox ):
        self.print_tree = print_tree
        self.type = None # object/support/enclosure/ raft
        self.outlines = []
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
        self.process_infill()

    def process_outlines(self, polygons):
        self.outlines.append(Outline(self, polygons))

    def process_shells(self):
        for outline in self.outlines:
            outline.make_shells()

    def process_infill(self):
        for outline in self.outlines:
            boundaries = outline.get_innershells()
            self.infill = Infill(boundaries,self.layers, self.layer_index,self.BBox)

    def process_upskins(self,):
        upislands = self.print_tree[self.index].islands
        intersect_layers()

    def process_skins(self, print_tree, layer_index):
        self.process_upskins()





    def g_print(self):
        printable_parts = []
        for outline in self.outlines:
            printable_parts += outline.g_print()
        printable_parts += self.infill.g_prtint()
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



