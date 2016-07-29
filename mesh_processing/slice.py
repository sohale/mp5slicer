import numpy as np
# from slicer.slicerCyth  import *

# slower
# def intersection_with_line(z, vertice_0, vertice_1):
#     if vertice_0[2] < vertice_1[2]:
#         low = vertice_1
#         high = vertice_0
#     else:
#         low = vertice_0
#         high = vertice_1

#     if z < high[2] or z > low[2]:
#         return None
#     else :
#         r = (z - low[2]) / (high[2] - low[2])
#         S = [low[0] + r * (high[0] - low[0]),
#              low[1] + r * (high[1] - low[1])]
#         return S

def intersection_with_line(z, vertice_0, vertice_1):
    v_0_x = vertice_0[0]
    v_0_y = vertice_0[1]
    v_0_z = vertice_0[2]
    
    v_1_x = vertice_1[0]
    v_1_y = vertice_1[1]
    v_1_z = vertice_1[2]

    if v_0_z < z: 
        if z < v_1_z:
            r = (z - v_0_z)/(v_1_z - v_0_z)
            s = [v_0_x + (v_1_x - v_0_x)*r, 
                 v_0_y + (v_1_y - v_0_y)*r]
            return s
        elif z > v_1_z:
            return None
        elif z == v_1_z:
            return [v_1_x, v_1_y]
        else:
            raise StandardError("this should be happen")
    elif v_0_z == z:
        return [v_0_x, v_0_y]
    elif z > v_1_z: # we know v_0_z > z  
        r = (z - v_1_z)/(v_0_z - v_1_z)
        s = [v_1_x + (v_0_x - v_1_x)*r, 
             v_1_y + (v_0_y - v_1_y)*r]
        return s
    elif z == v_1_z: # we know v_0_z > z and z <= v_1_z, the only possible way to has answer here is when z == v_1_z
        if v_0_z < v_1_z: # order for trim dict
            return [v_0_x, v_1_x]
        else:
            return [v_1_x, v_0_x]
    else:
        return None

def intersection_with_triangle(z, triangle):
    # triangle is a 3*3 
    assert isinstance(triangle, np.ndarray)
    # if(np.array_equal(triangle[0],triangle[1])):
    #     return []
    # if(np.array_equal(triangle[0],triangle[2])):
    #     return []
    # if(np.array_equal(triangle[2],triangle[1])):
    #     return []


    vertice_0 = triangle[0]
    vertice_1 = triangle[1]
    vertice_2 = triangle[2]

    # this is dealed with in the intersection by line
    # if vertice_0[2] == z:
    #     if vertice_1[2] == z:
            # not necessary since the triangle are repaired
            # if  vertice_2[2] != z: 
            #     return [vertice_0,vertice_1]
            # else:
            #     return None
        #     return [vertice_0,vertice_1]
        # if vertice_2[2] == z:
        #         return [vertice_0,vertice_2]
        # not necessary since the triangle are repaired
        # else:
            # return None
    # if vertice_1[2] == z:
    #     if vertice_2[2] == z:
            # not necessary since the triangle are repaired
            # if  vertice_0[2] != z:
            #     return [vertice_1,vertice_2]
            # else:
            #     return None
            # return [vertice_1,vertice_2]

    line = []

    intersection_point_0 = intersection_with_line(z, vertice_0, vertice_1)

    if intersection_point_0 is not None :
        line.append(intersection_point_0)


    intersection_point_1 = intersection_with_line(z, vertice_1, vertice_2)
    if intersection_point_0 == None: # line is empty so this must be one intersection point
            line.append(intersection_point_1)
    else:
        if intersection_point_1 is not None:
            line.append(intersection_point_1)

    if len(line) == 2:
        return line

    # if the line has not returned means there is noly one intersection point here
    intersection_point_2 = intersection_with_line(z, vertice_0, vertice_2)
    line.append(intersection_point_2)
    return line 
    # if intersection_point_2 is not None :
    #     if not np.array_equal(intersection_point_2,intersection_point_0) and not np.array_equal(intersection_point_1,intersection_point_2):
    #         line.append(intersection_point_2)
    # if len(line) == 1:
    #     raise RuntimeError
    # if len(line) != 2:
    #     raise RuntimeError


    # return line


def min_max_z(triangle):
    return [np.min(triangle[:,2]), np.max(triangle[:,2])]


def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return float('{0:.{1}f}'.format(f, n))
    i, p, d = s.partition('.')
    return float('.'.join([i, (d+'0'*n)[:n]]))


def slicer_from_mesh_as_dict_cy(mesh, slice_height_from=0, slice_height_to=100, slice_step=1):
    return slicer_from_mesh_as_dict_cyth(mesh, slice_height_from, slice_height_to, slice_step, sliceplanes_height=[])



def slicer_from_mesh_as_dict(mesh, slice_height_from=0, slice_height_to=100, slice_step=1, sliceplanes_height=[]):

    import datetime
    start_time = datetime.datetime.now()

    slice_height_from += 0.198768976
    slice_height_to += 0.198768976

    if sliceplanes_height != []: # if empty
        sliceplanes_height = sliceplanes_height
        sliceplanes_height = np.array(sliceplanes_height)
    else:
        sliceplanes_height = np.arange(slice_height_from, slice_height_to, slice_step)

    slice_layers = [{} for i in range(len(sliceplanes_height))]
    plane_index_list = np.array(range(len(slice_layers)))

    z = mesh.triangles[:,:,2]
    tri_min_list, tri_max_list = np.amin(z, axis=1), np.amax(z, axis=1)
    index_list = range(len(mesh.triangles))
    for triangle_index in range(len(mesh.triangles)):
        triangle = mesh.triangles[triangle_index]
        tri_min, tri_max = tri_min_list[triangle_index], tri_max_list[triangle_index]

        plane_index = plane_index_list[(tri_min<=sliceplanes_height)&(sliceplanes_height<=tri_max)]
        intersect_planes_heights = sliceplanes_height[plane_index]

        for index, z in zip(plane_index, intersect_planes_heights):
            line = intersection_with_triangle(z, triangle)
            # for point_index in range(len(line)):
            #     for val_index in range(len(line[point_index])):
            #         line[point_index][val_index] = truncate(line[point_index][val_index],8)

            point1 = tuple(line[0])
            point2 = tuple(line[1])

            try:
                if point2 not in slice_layers[index][point1]:
                    slice_layers[index][point1].append(point2)
            except KeyError:
                slice_layers[index][point1] = []
                slice_layers[index][point1].append(point2)
            try:
                if point1 not in slice_layers[index][point2]:
                    slice_layers[index][point2].append(point1)
            except KeyError:
                slice_layers[index][point2] = []
                slice_layers[index][point2].append(point1)
    return slice_layers

def visualization_3d(slice_layers):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for each_layer in slice_layers:
        for line_segment in each_layer:
            ax.plot([line_segment[0][0], line_segment[1][0]],
                    [line_segment[0][1], line_segment[1][1]],
                    zs=[line_segment[0][2], line_segment[1][2]])
    plt.show()

def visualization_2d(slice_layers):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D


    number_layers = len(slice_layers)
    number_row = int(np.ceil(np.sqrt(number_layers)))
    fig, axarr = plt.subplots(number_row, number_row, sharey=True)


    count = 0
    for each_layer in slice_layers:
        row_now = int(np.floor(count/number_row))
        column_now = int(count % number_row)
        for line_segment in each_layer:
            axarr[row_now, column_now].plot([line_segment[0][0], line_segment[1][0]], [line_segment[0][1], line_segment[1][1]])
        count += 1

    plt.show()

def adaptive_slicing(mesh, default_layer_thickness, curvature_tol=0.6, cusp_height_tol=0.15, layer_thickness_choices=[0.2, 0.15, 0.1], does_visualize = False):
    assert len(layer_thickness_choices) == 3

    '''
    This adative height calculation is based on cusp height and curvature, 
    it allows user for inputting three choice of layerthickness.

    The idea is simple, if certain triangle has curvature larger than curvature_tol or cusp_height_tol larger than cusp_height_tol,
    then if slice plane step trought this triangle, the slice plane should take a difference layer_thickness.

    Note since cusp_height calculation involves layerThickness, but there is impossible to know the layerThickness beforehand, thus 
    an assume layerThickness is used for cusp_height approximation.

    Explaination of cusp height can be found in paper Slicing_procedures_for_layered_manufacturing. 
    Cusp height and curvature calculation formula is found in paper part orientation and build cost determination in layer maufacturing.
    '''
    def extract_triangles_feature():

        average_layer_thickness = 0.2 # this is just for approximate cusp_height calculation
        triangle_counter = 0
        triangle_feature_recorder = {}

        for triangle in mesh.triangles:
            tri_min, tri_max = min_max_z(triangle)
            if tri_min != tri_max: # not consider weird triangle
                triangle_feature = 0

                normal = mesh.normals[triangle_counter]
                normal = normal/np.linalg.norm(normal)
                curvature = abs(np.dot(normal, [0,0,1]))
                cusp_height = curvature * average_layer_thickness
                triangle_counter += 1

                if curvature > curvature_tol:
                    triangle_feature += 1
                if cusp_height > cusp_height_tol:
                    triangle_feature += 1

                if triangle_feature > 0:
                    try:
                        if triangle_feature_recorder[(tri_min, tri_max)] < triangle_feature:
                            triangle_feature_recorder[(tri_min, tri_max)] = triangle_feature
                    except KeyError: # not define yet
                        triangle_feature_recorder[(tri_min, tri_max)] = triangle_feature


        return triangle_feature_recorder

    # import itertools
    triangle_feature_recorder = extract_triangles_feature()
    triangle_feature_recorder = [[i[0],i[1],triangle_feature_recorder[i]] for i in list(triangle_feature_recorder)]

    number_point = [i[0] for i in triangle_feature_recorder] + [i[1] for i in triangle_feature_recorder]
    number_point = sorted(set(number_point))

    '''
    range_feature_list is a list with lists. 
    For each list, it indicates the start range, end range and the feature of triangle, feature of triangle takes value 0, 1, 2.
    Feature of triangle is 0 if this trangle don't have high curvature and high cusp height.
    Feature of triangle is 1 if this trangle have either high curvature or high cusp height.
    Feature of triangle is 2 if this trangle have both high curvature and high cusp height.
    For example,
    range_feature_list = [[1,2,0],[3,5,2],[6,7,1]]
    Be aware that the third entry of each list is triangle feature, 
    it takes value 0, 1, 2 each indicates a thickness require for this triangle
    '''

    range_feature_list = []
    for i in range(len(number_point)-1): # this loop could be speed up
        feature = 0
        mid_point = (number_point[i] + number_point[i+1])/2
        for range_start, range_end, tri_feature in triangle_feature_recorder:
            if range_start <= mid_point <= range_end and feature < tri_feature:
                feature = tri_feature
            if feature == 2:
                break
        range_feature_list.append([number_point[i], number_point[i+1],feature])

    current_height = 0
    slice_plane_height = []
    thickness_list = []

    current_height = 0
    for _range in range_feature_list:# result_last = [start_range, end_range, triangle feature]
        start = _range[0]
        end = _range[1]
        feature = _range[2] # feature takes value 0, 1, 2
        while current_height <= end:
            if start <= current_height:
                '''
                Since feature takes value 0, 1, 2 and it is decided to be 
                coincident with the length of layer_thickness_choices and position.
                '''
                current_height += layer_thickness_choices[feature] 
                slice_plane_height.append(current_height)
                thickness_list.append(layer_thickness_choices[feature])
            else: 
                current_height += default_layer_thickness
                slice_plane_height.append(current_height)
                thickness_list.append(layer_thickness_choices[feature])

    # pass the range of range_feature_list but not reach the mesh zmax
    while current_height < mesh.bounding_box().zmax - default_layer_thickness - 0.000001: # 0.000001 is for just in case the current_height is exactly the same to the top of the mesh
        current_height += default_layer_thickness
        slice_plane_height.append(current_height)
        thickness_list.append(layer_thickness_choices[feature])

    ################### visualisation ###################
    if does_visualize:
        import matplotlib.pyplot as plt
        from matplotlib import collections  as mc
        lines = [((0,height),(5,height)) for height in slice_plane_height]
        c = []
        for thickness in thickness_list:
            if thickness == layer_thickness_choices[0]:
                c.append('r')
            elif thickness == layer_thickness_choices[1]:
                c.append('b')
            elif thickness == layer_thickness_choices[2]:
                c.append('g')
            else:
                raise RuntimeError

        lc = mc.LineCollection(lines, color = c, linewidths=thickness_list)
        fig, ax = plt.subplots()
        ax.add_collection(lc)
        ax.autoscale()
        ax.margins(0.1)

        import matplotlib.patches as mpatches
        red_patch = mpatches.Patch(color='r', label='large thickness')
        blue_patch = mpatches.Patch(color='b', label='middle thickness')
        green_patch = mpatches.Patch(color='g', label='small thickness')

        plt.legend(handles=[red_patch, blue_patch, green_patch])
        plt.show()

    return slice_plane_height, thickness_list

if __name__ == '__main__':
    # import datetime
    # start = datetime.datetime.now()
    # slice_layers = slicer('FLATFOOT_StanfordBunny_jmil_HIGH_RES_Smoothed.stl', slice_height_from=0, slice_height_to=100, slice_step=1)
    # print(datetime.datetime.now() - start)
    # visualization_2d(slice_layers)
    from stl import mesh
    from mesh_operations import mesh as MPmesh

    stl_mesh = mesh.Mesh.from_file('elephant.stl')
    this_mesh = MPmesh(stl_mesh.vectors, fix_mesh= True)
    # print(max_curvature_for_this_layer(this_mesh, 12))
    # print(maximum_cusp_height_for_this_layer(this_mesh, 12, 0.2))
    # z_values = adative_height(this_mesh, 0.2)
    # slice_layers = slicer_from_mesh_as_dict(this_mesh, sliceplanes_height = [])
