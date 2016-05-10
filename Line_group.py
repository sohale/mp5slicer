

class Line_group():

    def __init__(self,type, width = 0):
        self.sub_lines = []
        self.type = type
        self.print_time = 0
        if (type == "skin" or type == "infill" or type == "boundary" or type == "hole" or type == "inner_boundary" or type == "inner_hole"):
            self.isLeaf = True
            assert (width != 0)
            self.width = width
        else:
            self.isLeaf = False


    def add_chain(self, line):
        assert (self.isLeaf)
        self.sub_lines.append(line)

    def add_group(self, group):
        assert(self.isLeaf == False)
        assert (isinstance(group, Line_group))
        self.sub_lines.append(group)