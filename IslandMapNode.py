


class IslandMapNode:
    def __init__(self,position,neighbours = [], poly=None, indexInPoly=None):
        """ initializes a graph object """
        self.position = position
        self.neighbours = neighbours
        self.poly = poly
        self.indexInPoly = indexInPoly

    def getNeighbours(self):
        return self.neighbours

    def addNeighbours(self,neighbours):
        self.neighbours += neighbours

    def addNeighbour(self, neighbour):
        self.neighbours.append(neighbour)

