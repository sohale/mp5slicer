class TreePostProcessor(object):

    def __init__(self, print_tree):
        self.print_tree = print_tree
        self.tasks = []

    def add_task(self, task, level=0):
        self.tasks.append(task)

    def run(self):
        for layer_index in range(len(self.print_tree)):
            self.layer_index = layer_index
            if len(self.print_tree[layer_index].sub_lines) != 0:
                self.__gotroughgroup(self.print_tree[layer_index])

    def __gotroughgroup(self, group):
        if group.isLeaf:
            self.__switch_leaf(group)
        else:
            self.__switch_node(group)

    def __switch_leaf(self, leaf):
        for task in self.tasks:
            method = getattr(task, 'leaf')
            method(leaf)

        for task in self.tasks:
            method = getattr(task, leaf.type)
            method(leaf)

    # @profile
    def __switch_node(self, node):
        for task in self.tasks:
            method = getattr(task, node.type)
            method(node)

        for sub_node in node.sub_lines:
            self.__gotroughgroup(sub_node)
