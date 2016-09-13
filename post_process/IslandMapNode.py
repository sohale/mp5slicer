class IslandMapNode(object):
    def __init__(self, position, neighbours={}, poly=None, index_in_poly=None):
        """ initializes a graph object """
        self.position = position
        self.neighbours = neighbours
        self.poly = poly
        self.index_in_poly = index_in_poly

    def get_neighbours(self):
        return self.neighbours

    def add_neighbour(self, neighbour, pos):
        self.neighbours[tuple(pos)] = neighbour