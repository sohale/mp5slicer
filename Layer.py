from Island import Island

class Layer():

    def __init__(self,layers, index,BBox):#layers are only passed as a reference to get an acces for skin processing
        self.layers = layers
        self.islands = []
        self.index = index
        self.BBox = BBox
        self.add_island()

    def G_print(self):
        for island in self.islands:
            return island.g_print()

    def process_shells(self):
        for island in self.islands:
            island.process_shells()

    def add_island(self):
        if len(self.layers[self.index]) != 0:
            island =Island(self.layers,self.index,self.BBox)
            self.islands.append(island)

