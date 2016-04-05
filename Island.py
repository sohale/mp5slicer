from pipeline_test import *
from Parts import *

class Island():
    def __init__(self,layer, layers,polygons,skin_polygons,layer_index,BBox ):
        self.layer = layer
        self.type = None # object/support/enclosure/ raft
        self.outline = []
        self.layer_index = layer_index
        self.layers = layers
        self.BBox = BBox
        self.get_parts(polygons,skin_polygons)

    def process_shells(self):
        self.outline.add_shells()




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

    def get_parts(self, polygons,skin_polygons):
        self.outline.append(self.make_outline(polygons))

        # if len(skin_polygons) != 0:
        #     # skins = self.make_skins(skin_polygons)
        #     # self.parts.append(skins)
        #     infill = self.make_infill_with_skins(polygons,skin_polygons)
        #     self.parts.append(infill)
        # else:
        #     infill = self.make_infill(polygons)
        #     self.parts.append(infill)



