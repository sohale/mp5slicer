from Island import Island

class Layer():

    def __init__(self):#layers are only passed as a reference to get an acces for skin processing
        self.islands = []

    def G_print(self):
        for island in self.islands:
            return island.g_print()

    def add_island(self,polygons):
        if len(polygons) != 0:
            island =Island(polygons)
            self.islands.append(island)

