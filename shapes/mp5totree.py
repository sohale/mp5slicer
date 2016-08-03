
from slicer.shapes.Boundingbox import *

def get_mc_params(mp5source):


    root_node = get_root_node(mp5source)
    bbox = get_fonuky(root_node)




    return bbox

    # display_simple_using_mayavi_2([(vertex_before_qem, faces), (new_vertex_qem, faces), ],
    #    pointcloud_list=[],
    #    mayavi_wireframe=[False, False], opacity=[0.4*0, 1, 0.9], gradients_at=None, separate=False, gradients_from_iobj=None,

def get_root_node(tree):
    return tree["root"]



def get_fonuky(node):
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

    }
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


def root(node):
    matrix = np.eye(4)
    result_bbox = Bbox(Coords(float("inf"), float("inf"), float("inf")),
                       Coords(float("-inf"), float("-inf"), float("-inf")))

    sons = node["children"]
    for i in range(len(sons)):
        sbbox = get_fonuky(sons[i])
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


