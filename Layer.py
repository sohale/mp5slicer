from Island import Island

class Layer():

    def __init__(self,layers, index,BBox):#layers are only passed as a reference to get an acces for skin processing
        self.layers = layers
        self.islands = []
        self.index = index
        self.BBox = BBox

    def G_print(self):
        for island in self.islands:
            return island.g_print()

    def add_island(self,polygons,skins):
        if len(polygons) != 0:
            island =Island(self.layers,polygons,skins,self.index,self.BBox)
            self.islands.append(island)

