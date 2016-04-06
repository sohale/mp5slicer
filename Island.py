from pipeline_test import *
from Parts import *

class Island():
    def __init__(self,layer, layers,polygons,layer_index,BBox ):
        self.layer = layer
        self.type = None # object/support/enclosure/ raft
        self.outlines = []
        self.layer_index = layer_index
        self.layers = layers
        self.BBox = BBox
        self.process_outlines(polygons)

    def process_shells(self):
        self.outline.make_shells()




    def g_print(self):
        printable_parts = []
        for part in self.parts:
            printable_parts += part.g_print()
        return  printable_parts

    def make_outline(self,polygons):
        outline = Outline(polygons)
        return outline

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

    def process_outlines(self, polygons):
        self.outline.append(self.make_outline(self,polygons))

        # if len(skin_polygons) != 0:
        #     # skins = self.make_skins(skin_polygons)
        #     # self.parts.append(skins)
        #     infill = self.make_infill_with_skins(polygons,skin_polygons)
        #     self.parts.append(infill)
        # else:
        #     infill = self.make_infill(polygons)
        #     self.parts.append(infill)



