from pipeline_test import *
from Parts import *

class Island():
    def __init__(self,polygons ):
        self.type = None # object/support/enclosure/ raft
        self.parts = []
        self.get_parts(polygons)

    def g_print(self):
        printable_parts = []
        for part in self.parts:
            printable_parts += part.g_print()
        return  printable_parts

    def make_outline(self,polygons):
        outline = Outline(polygons)
        return outline

    def make_skins(self,polygons,top_layer):
        pass

    def make_infill_with_skins(self,polygons,skins):
        pass

    def make_infill(self,polygons):
        pass

    def get_parts(self, polygons):
        self.parts.append(self.make_outline(polygons))
        # skins = self.make_skins(polygons)
        # if skins != None:
        #     self.parts.append(skins)
        #     infill = self.make_infill_with_skins(polygons,skins)
        #     self.parts.append(infill)
        # else:
        #     infill = self.make_infill(polygons)
        #     self.parts.append(infill)



