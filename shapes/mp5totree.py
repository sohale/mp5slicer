
from slicer.shapes.Boundingbox import *

def get_mc_params(mp5source, son_position):


    root_node = get_root_node(mp5source)
    bbox = get_fonuky(root_node, son_position)




    return bbox

def get_root_node(tree):
    return tree["root"]



def get_fonuky(node, params = None):
    type = node["type"]


    switch = {
        "Difference": subtract,
        "cylinder": cylinder,
        "icylinder": cylinder,
        "icone": cone,
        "iellipsoid": ellipsoid,
        "icube": cube,
        "root" : root,
        "Union" : union,
        "Intersection": intersection,
        "itorus": torus,

    }
    if params is not None:
        bbox = switch[type](node, params)
    else :
        bbox = switch[type](node)
    return bbox


def subtract(node):
    matrix = make_matrix4(node["matrix"])
    result_bbox = Bbox(Coords(float("inf"), float("inf"), float("inf")),
                       Coords(float("-inf"), float("-inf"), float("-inf")))

    sons = node["children"]
    for i in range(len(sons)):
        sbbox = get_fonuky(sons[i])
        result_bbox = updateBoundingBoxForSubBoundingBox(result_bbox, None, sbbox)  # just update, dont apply the matrix

    bbox = updateBoundingBoxForSubBoundingBox(None, matrix, result_bbox)
    return bbox

def intersection(node):
    matrix = make_matrix4(node["matrix"])
    result_bbox = Bbox(Coords(float("inf"), float("inf"), float("inf")),
                       Coords(float("-inf"), float("-inf"), float("-inf")))

    sons = node["children"]
    for i in range(len(sons)):
        sbbox = get_fonuky(sons[i])
        result_bbox = updateBoundingBoxForSubBoundingBox(result_bbox, None, sbbox)  # just update, dont apply the matrix

    bbox = updateBoundingBoxForSubBoundingBox(None, matrix, result_bbox)
    return bbox

def union(node):
    matrix = make_matrix4(node["matrix"])
    result_bbox = Bbox(Coords(float("inf"), float("inf"), float("inf")),
                       Coords(float("-inf"), float("-inf"), float("-inf")))

    sons = node["children"]
    for i in range(len(sons)):
        sbbox = get_fonuky(sons[i])
        result_bbox = updateBoundingBoxForSubBoundingBox(result_bbox, None, sbbox)  # just update, dont apply the matrix

    bbox = updateBoundingBoxForSubBoundingBox(None, matrix, result_bbox)
    return bbox

def cube(node):
    matrix = make_matrix4(node["matrix"])
    bbox = getBoundingBoxForSingleShapeMatrix(matrix)

    return bbox

def ellipsoid(node):
    matrix = make_matrix4(node["matrix"])
    bbox = getBoundingBoxForSingleShapeMatrix(matrix)

    return bbox

def cone(node):
    matrix = make_matrix4(node["matrix"])
    bbox = getBoundingBoxForSingleShapeMatrix(matrix)

    return bbox

def cylinder(node):
    matrix = make_matrix4(node["matrix"])
    bbox = getBoundingBoxForSingleShapeMatrix(matrix)

    return bbox

def torus(node):
    matrix = make_matrix4(node["matrix"])
    bbox = getBoundingBoxForSingleShapeMatrix_torus(matrix)

    return bbox


def root(node, son_position):
    matrix = np.eye(4)
    result_bbox = Bbox(Coords(float("inf"), float("inf"), float("inf")),
                       Coords(float("-inf"), float("-inf"), float("-inf")))

    # sons = node["children"]
    # for i in range(len(sons)):
    #     sbbox = get_fonuky(sons[i])
    #     result_bbox = updateBoundingBoxForSubBoundingBox(result_bbox, None, sbbox)  # just update, dont apply the matrix

    sons = node["children"]

    sbbox = get_fonuky(sons[son_position])
    result_bbox = updateBoundingBoxForSubBoundingBox(result_bbox, None, sbbox)  # just update, dont apply the matrix

    bbox = updateBoundingBoxForSubBoundingBox(None, matrix, result_bbox)
    return bbox

def make_matrix4(array):
    arr = np.array(array).astype(float)
    return np.matrix(np.reshape(arr, (4,4)))



# class node():
#
#     def __init__(self,sons, type, matrix):
#         self.type = type
#         self.sons =sons
#         self.matrix = matrix
#
#
#     def is_leaf(self):
#         return (self.type == 'Difference' or self.type == "mescouilles")
#
#     def add_son(self, node):
#         self.sons.append(node)


