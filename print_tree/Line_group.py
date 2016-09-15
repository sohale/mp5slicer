class LineGroup(object):

    def __init__(self, type, is_leaf, width=0):
        self.sub_lines = []
        self.type = type
        self.properties = {}
        self.is_leaf = is_leaf
        if self.is_leaf:
            assert (width != 0)
            self.width = width
        else:
            self.is_leaf = False

    def add_chain(self, line):
        assert (self.is_leaf)
        self.sub_lines.append(line)

    def add_chains(self, lines):
        assert (self.is_leaf)
        self.sub_lines.extend(lines)

    def add_group(self, group):
        assert(self.is_leaf is False)
        assert (isinstance(group, LineGroup))
        self.sub_lines.append(group)
