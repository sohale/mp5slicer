import Island

class Layer():
    islands = []
    def __init__(self,layer_index,layers):#layers are only passed as a reference to get an acces for skin processing

        pass

    def G_print(self):
        for island in self.islands:
            return island.g_print()

    def add_island(self,index,polygons):
        island =Island(polygons)
        self.islands.append(island)

