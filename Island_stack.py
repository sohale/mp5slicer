


class Island_stack():

    def __init__(self, polynode):
        self.islands = []
        self.split(polynode)

    def split(self,polynode):
        for child in polynode.Childs:
            if not child.IsHole:
                self.islands.append(child)
                if child.depth > 0:
                    self.split(child)
            elif child.depth > 0:
                self.split(child)

    def get_islands(self):
        return self.islands

