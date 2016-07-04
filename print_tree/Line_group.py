

class Line_group():

    def __init__(self,type, isLeaf, width = 0):
        self.sub_lines = []
        self.type = type
        self.properties = {}
        self.isLeaf = isLeaf
        if self.isLeaf:
            assert (width != 0)
            self.width = width
        else:
            self.isLeaf = False


    def add_chain(self, line):
        assert (self.isLeaf)
        self.sub_lines.append(line)

    def add_chains(self, lines):
        assert (self.isLeaf)
        self.sub_lines.extend(lines)

    def add_group(self, group):
        assert(self.isLeaf == False)
        assert (isinstance(group, Line_group))
        self.sub_lines.append(group)