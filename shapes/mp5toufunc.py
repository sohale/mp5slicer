import numpy as np
from implisolid.clean_code.basic_functions import make_vector4
from implisolid.clean_code import vector3


def get_root_node(tree):
    return tree["root"]


def get_fonuky(node):
    type = node["type"]

    switch = {
        "Difference": crisp_subtract,
        "cylinder": simple_cylinder,
        "root": root,

    }
    ufunc = switch[type](node)
    return ufunc


def crisp_subtract(node):

    sons = node["children"]
    son1 = get_fonuky(sons[0])
    son2 = get_fonuky(sons[1])
    matrix = make_matrix4(node["matrix"])
    return vector3.Transformed(vector3.CrispSubtract(son1, son2), matrix)


def simple_cylinder(node):
    matrix = make_matrix4(node["matrix"])
    A = make_vector4(-0.5, 0, 0)
    w = make_vector4(0, 0, 1)
    u = make_vector4(1, 0, 0)
    return vector3.Transformed(
        vector3.SimpleCylinder(A, w, u, 0.5, 0.5, 1), matrix)


def root(node):
    sons = node["children"]
    return get_fonuky(sons[0])


def make_matrix4(array):
    arr = np.array(array).astype(float)
    return np.reshape(arr, (4, 4))


#
# class node(object):
#
#     def __init__(self, type, matrix):
#         self.type = type
#         self.sons =[]
#         self.matrix = matrix
#
#
#     def is_leaf(self):
#         return (self.type == 'Difference' or self.type == "mescouilles")
#
#     def add_son(self, node):
#         self.sons.append(node)


