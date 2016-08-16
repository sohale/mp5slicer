import  numpy as np
import copy

class Coords():
    def __init__(self, x, y ,z):
        self.x= x
        self.y = y
        self.z = z

class Bbox():
    def __init__(self, min , max ):
        self.min = min
        self.max = max


def getBoundingBoxForTree (shape, ignore_root_matrix) :
    # //if(result_bbox === null) {

    if(isSingleShape(shape)) :

        return getBoundingBoxForSingleShapeMatrix(shape.matrix)

    elif (isTree(shape)) :

        result_bbox = Bbox(Coords(float("inf"),float("inf"),float("inf")), Coords(float("-inf"),float("-inf"),float("-inf")))

        for i  in range( 0, shape.sons.length) :
            sbbox = getBoundingBoxForTree(shape.sons[i], False) # never ignore the matrix if not root
            updateBoundingBoxForSubBoundingBox(result_bbox, None,  sbbox)  # just update, dont apply the matrix

        ret = updateBoundingBoxForSubBoundingBox(None, shape.matrix ,  result_bbox)
        return ret

    else :
        print("not a shape neither a tree")

    # //return result_bbox;



def getBoundingBoxForSingleShapeMatrix(this_matrix) :
    pass
#

    result_bbox = Bbox(Coords(float("inf"),float("inf"),float("inf")), Coords(float("-inf"),float("-inf"),float("-inf")))


    v = np.array([0, 0, 0,1])
    v = np.reshape(v,(4,1))

    for x in [-0.5, 0.5]:
        for y in [-0.5, 0.5]:
            for z in [-0.5, 0.5]:
                v[0] = x
                v[1] = y
                v[2] = z

                v = np.matmul(this_matrix,v)

                new_x = copy.copy(v[0])
                new_y = copy.copy(v[1])
                new_z = copy.copy(v[2])

                if (new_x < result_bbox.min.x): result_bbox.min.x = new_x
                if (new_y < result_bbox.min.y): result_bbox.min.y = new_y
                if (new_z < result_bbox.min.z): result_bbox.min.z = new_z
                if (new_x > result_bbox.max.x): result_bbox.max.x = new_x
                if (new_y > result_bbox.max.y): result_bbox.max.y = new_y
                if (new_z > result_bbox.max.z): result_bbox.max.z = new_z
    return result_bbox

def getBoundingBoxForSingleShapeMatrix_torus(this_matrix) :
    pass
#

    result_bbox = Bbox(Coords(float("inf"),float("inf"),float("inf")), Coords(float("-inf"),float("-inf"),float("-inf")))


    v = np.array([0, 0, 0,1])
    v = np.reshape(v,(4,1))

    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-0.5, 0.5]:
                v[0] = x
                v[1] = y
                v[2] = z

                v = np.matmul(this_matrix,v)

                new_x = copy.copy(v[0])
                new_y = copy.copy(v[1])
                new_z = copy.copy(v[2])

                if (new_x < result_bbox.min.x): result_bbox.min.x = new_x
                if (new_y < result_bbox.min.y): result_bbox.min.y = new_y
                if (new_z < result_bbox.min.z): result_bbox.min.z = new_z
                if (new_x > result_bbox.max.x): result_bbox.max.x = new_x
                if (new_y > result_bbox.max.y): result_bbox.max.y = new_y
                if (new_z > result_bbox.max.z): result_bbox.max.z = new_z
    return result_bbox

#
# /* Multiplies the this_matrix into input_sbbox and updates result_bbox
# */
def updateBoundingBoxForSubBoundingBox (result_bbox, this_matrix, input_sbbox) :

    if(result_bbox is None) :
        result_bbox = Bbox(Coords(float("inf"),float("inf"),float("inf")), Coords(float("-inf"),float("-inf"),float("-inf")))

    if this_matrix is None:
        this_matrix = np.eye(4)
    v = np.array([0,0,0,1]).astype(dtype=np.float)
    v = np.reshape(v,(4,1))

    for xi in [0,1]:
        x = input_sbbox.min.x if (xi==0) else (input_sbbox.max.x)

        for yi in [0,1]:
            y = input_sbbox.min.y if (yi==0) else (input_sbbox.max.y)

            for zi in [0,1]:
                z = input_sbbox.min.z if (zi==0) else (input_sbbox.max.z)
                v[0]  = x.item(0)
                v[1]  = y.item(0)
                v[2]  = z.item(0)

                v = np.matmul(this_matrix,v)
                new_x = copy.copy(v[0])
                new_y = copy.copy(v[1])
                new_z = copy.copy(v[2])

                if(new_x < result_bbox.min.x): result_bbox.min.x = new_x
                if(new_y < result_bbox.min.y): result_bbox.min.y = new_y
                if(new_z < result_bbox.min.z): result_bbox.min.z = new_z
                if(new_x > result_bbox.max.x): result_bbox.max.x = new_x
                if(new_y > result_bbox.max.y): result_bbox.max.y = new_y
                if(new_z > result_bbox.max.z): result_bbox.max.z = new_z





    return result_bbox

# /** end ShapeTree **/
#
#
# function get_bbox_centre(bbox) {
#     // todo: reuse the object (avoid gc)
#     return new Vector3D(
#             (bbox.min.x + bbox.max.x) / 2,
#             (bbox.min.y + bbox.max.y) / 2,
#             (bbox.min.z + bbox.max.z) / 2
#         );
# }
#
# function bbox_to_list(input_sbbox) {
#     var list = [];
#     var x, y, z;
#     for(var xi=0; xi <= 1; xi++) {
#         x = (xi==0) ? (input_sbbox.min.x) : (input_sbbox.max.x);
#
#         for(var yi=0; yi < 2; yi++) {
#             y = (yi==0) ? (input_sbbox.min.y) : (input_sbbox.max.y);
#
#             for(var zi=0; zi < 2; zi++) {
#                 z = (zi==0) ? (input_sbbox.min.z) : (input_sbbox.max.z);
#
#                 list.push(x);
#                 list.push(y);
#                 list.push(z);
#             }
#
#         }
#
#     }
#     return list;
# }

treemap = ["ShapeTree",
           "SimpleShapeTree",
           "ToolTree"]


shapemap = [ "Rectangle",
             "Ellipse",
             "Ellipsoid",
             "Cone",
             "Cuboid",
             "StandingCylinder",
             "Shape2D",
             "SingleShape3D",
             ]


# function isTree(obj)
# {
#     for (var i = 0; i < treemap.length; i++)
#     {
#         if (obj instanceof treemap[i][0])
#         {
#             return true;
#         }
#     }
#
#     return false;
# }

def isTree(obj):

    for i in range(len(shapemap)):
        if (isinstance(obj, shapemap[i])):
            return True;

    return False

def isSingleShape(obj):

    for i in range(len(shapemap)):
        if (isinstance(obj, shapemap[i])):
            return True;

    return False
