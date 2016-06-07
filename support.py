'''
This file is for support algorithms.
'''

import inspect, os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

import numpy as np
import slicer.config as config
# support point sampling

def ray_triangle_intersection(ray_near, triangle):
    """
    Taken from Printrun
    Möller–Trumbore intersection algorithm in pure python
    Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    
    ray_dir is set as [[0],[0],[-1]] for optimizing running speed
    ray_near should be the origin of this ray.
    """
    
    v1 = triangle[0]
    v2 = triangle[1]
    v3 = triangle[2]
    ray_dir = np.asarray([0,0,-1]) # column vector to row vector
    
    eps = 0.000001
    edge1 = v2 - v1
    edge2 = v3 - v1
    pvec = [edge2[1],-edge2[0],0] # pvec = np.cross(ray_dir, edge2)
    det = edge1[0]*pvec[0]+ edge1[1]*pvec[1] # det = edge1.dot(pvec)
    if abs(det) < eps:
        return False, None
    inv_det = 1. / det
    tvec = ray_near - v1
    u = (tvec[0]*pvec[0]+tvec[1]*pvec[1]) * inv_det # u = tvec.dot(pvec) * inv_det
    if u < 0. or u > 1.:
        return False, None
    qvec = np.cross(tvec, edge1)
    v = ray_dir.dot(qvec) * inv_det
    if v < 0. or u + v > 1.:
        return False, None
    t = edge2.dot(qvec) * inv_det
    if t < eps:
        return False, None

    # point = ray_near + ray_dir*t
    # z_value = point[2]
    z_value = ray_near[2] - t

    return True, z_value

# don't delele, this is the general version of the ray trace algorithm.
# def ray_triangle_intersection_old(ray_near, ray_dir, triangle):
#     """
#     Taken from Printrun
#     Möller–Trumbore intersection algorithm in pure python
#     Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    
#     ray_near should be the origin of this ray.
#     """
    
#     v1 = triangle[0]
#     v2 = triangle[1]
#     v3 = triangle[2]
#     ray_dir = np.asarray([0,0,-1]) # column vector to row vector
    
#     eps = 0.000001
#     edge1 = v2 - v1
#     edge2 = v3 - v1
#     pvec = np.cross(ray_dir, edge2)
#     det = edge1.dot(pvec)
#     if abs(det) < eps:
#         return False, None
#     inv_det = 1. / det
#     tvec = ray_near - v1
#     u = tvec.dot(pvec) * inv_det
#     if u < 0. or u > 1.:
#         return False, None
#     qvec = np.cross(tvec, edge1)
#     v = ray_dir.dot(qvec) * inv_det
#     if v < 0. or u + v > 1.:
#         return False, None
#     t = edge2.dot(qvec) * inv_det
#     if t < eps:
#         return False, None

#     point = ray_near + ray_dir*t
#     z_value = point[2]

#     return True, z_value

def dot_building_direction(mesh):

    # this function assuming the building_direction = [[0],[0],[1]] since it save a lot of time
    # the dot product 
    from numpy import linalg as LA
    norms = np.apply_along_axis(LA.norm, 1, mesh.normals)
    dot_product = mesh.normals[:,2] # faster than np.apply_along_axis(np.dot, 1, normals, [[0],[0],[1]])
    return dot_product/norms

def revert_sort_by_z(mesh):
    # z : are a list of z values from trangles
    # returns index for mininum z in descending order
    z = mesh.vectors[:,:,2]
    min_z_order = np.argsort(np.amin(z, axis=1)) 
    # index of minimum z coord of each triangle
    min_z_order = min_z_order[::-1]
    return min_z_order

def triangle_center(mesh):
    centers = (mesh.vectors[:, 0] + mesh.vectors[:, 1] + mesh.vectors[:, 2])/3 # (vertex 0 + vertex 1 + vertex 2)/3
    return centers

def detect_support_requiring_facet(mesh, cos_angle_threshold, bed_height, support_starts_height = 0.3):
    
    def min_z(mesh):
        return np.min(mesh.triangles[:,:,2], axis=1) # min z of each triangles

    # threshold is cos(theta) value
    # if building_direction is vector [[0], [0], [1]]
    # if threshold is cos(-135 degree) = sqrt(2)/2 = -0.70710678118, means if angle is between 135 and 225 degree then these facet requres support
    normal_cos_theta = dot_building_direction(mesh)
    exceed_threshold_mask = (normal_cos_theta<cos_angle_threshold) # boolean list indicating which triangle requires support 

    # also ignore the facet too close to the bed
    not_too_close_to_bed_mask = (min_z(mesh) > bed_height + support_starts_height)
    support_required_mask = np.logical_and(exceed_threshold_mask, not_too_close_to_bed_mask)

    return support_required_mask # returns a boolen list indicated which triangles require support

def group_support_area(mesh, support_required_mask):

    import datetime
    start_time = datetime.datetime.now()

    support_triangles = mesh.triangles[support_required_mask]
    support_triangles = np.around(support_triangles, decimals = 1)

    print('number of triangles')
    print(len(support_triangles))
    triangle_index_and_its_neighbour = {}


    for tri_index in range(len(support_triangles)):
        neighbour = set()
        triangle_index_and_its_neighbour[tri_index] = neighbour

        triangle = support_triangles[tri_index]
        x = list(triangle[0])
        y = list(triangle[1])
        z = list(triangle[2])

        for tri_detect_index in range(len(support_triangles)):

            if tri_detect_index in triangle_index_and_its_neighbour and tri_index in triangle_index_and_its_neighbour[tri_detect_index]:
                neighbour.add(tri_detect_index)
                continue

            tri = support_triangles[tri_detect_index]

            x_test = list(tri[0])
            y_test = list(tri[1])
            z_test = list(tri[2])

            if x == x_test:
                neighbour.add(tri_detect_index)
                continue # check for next triangle, this triangle is already a neighbour, no need to check further
            elif x == y_test:
                neighbour.add(tri_detect_index)
                continue
            elif x == z_test:
                neighbour.add(tri_detect_index)
                continue
            elif y == x_test:
                neighbour.add(tri_detect_index)
                continue
            elif y == y_test:
                neighbour.add(tri_detect_index)
                continue
            elif y == z_test:
                neighbour.add(tri_detect_index)
                continue
            elif z == x_test:
                neighbour.add(tri_detect_index)
                continue
            elif z == y_test:
                neighbour.add(tri_detect_index)
                continue
            elif z == z_test:
                neighbour.add(tri_detect_index)
                continue
            else:
                pass

        neighbour.remove(tri_index)
    # group them together by connected group component algorithm 
    # from http://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/

    def dfs(graph, start):
        visited, stack = set(), [start]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                stack.extend(graph[vertex] - visited)
        return visited

    groups = []
    support_indexs = set(triangle_index_and_its_neighbour)
    while support_indexs:
        start = support_indexs.pop()
        visited = dfs(triangle_index_and_its_neighbour, start)

        group = list(visited)
        groups.append(group)

        support_indexs = support_indexs - visited

    print('-------len of group-----------')
    print(len(groups))

    print(start_time)
    print(datetime.datetime.now())

    print('------- grouping time -------------')
    print(datetime.datetime.now() - start_time)
    return groups


def sampling_support_points(mesh, support_required_mask, groups, sampling_distance):

    triangles = mesh.triangles[support_required_mask]

    for group in groups:
        group_tri = triangles[group]
        group_0 = np.array(group_tri)

        min_x =  np.min(np.min(group_0[:,:,0]))
        max_x =  np.max(np.max(group_0[:,:,0]))
        min_y =  np.min(np.min(group_0[:,:,1]))
        max_y =  np.max(np.max(group_0[:,:,1]))
        min_z = np.min(np.min(group_0[:,:,2]))
        max_z = np.max(np.max(group_0[:,:,2]))

        # sampling in x, y plane
        x_sample = np.arange(min_x, max_x, sampling_distance)
        y_sample = np.arange(min_y, max_y, sampling_distance)

        def ray_trace_mesh(ray, mesh):
            tri_index = 0
            for triangle in mesh:
                res = ray_triangle_intersection(ray, triangle)
                if res[0]:
                    return res[1] , tri_index # should only be one z value # index is for support only
                tri_index += 1

        support_points = []
        epsilon = 0.01
        for x in x_sample:
            for y in y_sample:
                res = ray_trace_mesh([x, y, max_z + epsilon], triangles)
                if res != None:
                    z = res[0]
                    support_points.append([x, y, z])
                else:
                    pass

    if len(groups) == 0:
        support_points = []
    else:
        pass

    return support_points

def max_z(mesh):
    return np.max(mesh.triangles[:,:,2], axis=1)

def min_z(mesh):
    return np.min(mesh.triangles[:,:,2], axis=1)

def min_x(mesh):
    return np.min(mesh.triangles[:,:,0], axis=1)

def max_x(mesh):
    return np.max(mesh.triangles[:,:,0], axis=1)

def min_y(mesh):
    return np.min(mesh.triangles[:,:,1], axis=1)

def max_y(mesh):
    return np.max(mesh.triangles[:,:,1], axis=1)

def self_support_detection(mesh, bounding_box, support_points):

    epsilon = 0.1

    ray_direction_vector = np.array([[0],[0],[-1]])

    bed_z = bounding_box.zmin
    min_z_list = min_z(mesh)
    min_x_list = min_x(mesh)
    max_x_list = max_x(mesh)
    min_y_list = min_y(mesh)
    max_y_list = max_y(mesh)

    z_triangle_selfsupport = [bed_z for i in range(len(support_points))]

    for index in range(len(support_points)):
        x = support_points[index][0]
        y = support_points[index][1]
        z = support_points[index][2]

        # mask_x = np.logical_not(np.logical_or(max_x_list<x-epsilon, min_x_list>x+epsilon))
        # mask_y = np.logical_not(np.logical_or(max_y_list<y-epsilon, min_y_list>y+epsilon))

        mask_x = np.logical_and(max_x_list>x, min_x_list<x)
        mask_y = np.logical_and(max_y_list>y, min_y_list<y)
        mask_z = (min_z_list<z-epsilon)


        for tri_index in np.where(mask_z&mask_x&mask_y)[0]:
            triangle = mesh.triangles[tri_index]
            res = ray_triangle_intersection(support_points[index], triangle)
            if res[0]:
                if res[1] > z_triangle_selfsupport[index]:
                    z_triangle_selfsupport[index] = res[1]
    return z_triangle_selfsupport   

def support_lines(mesh, sampling_distance):

    bounding_box = mesh.bounding_box()
    bed_level = bounding_box.zmin

    cos_angle_threshold = -0.9
    support_required_mask = detect_support_requiring_facet(mesh, cos_angle_threshold, bed_level)
    groups = group_support_area(mesh, support_required_mask)
    support_points = sampling_support_points(mesh, support_required_mask, groups, sampling_distance)
    self_support_z_values = self_support_detection(mesh, bounding_box, support_points)
    

    support_points_starts_list = []
    support_points_ends_list = []

    for support_point, self_support_z in zip(support_points, self_support_z_values):
        x = support_point[0]
        y = support_point[1]
        z = support_point[2]
        support_points_starts_list.append([x, y, self_support_z])
        support_points_ends_list.append([x, y, z])

    return support_points_starts_list, support_points_ends_list

def arranged_polyline_from_support(support_points_starts_list, support_points_ends_list, height, layerthickness):
    intersect_points = []
    for point_start, point_end in zip(support_points_starts_list, support_points_ends_list):
        point_start_x = point_start[0]
        point_start_y = point_start[1]
        point_start_z = point_start[2]
        point_end_x = point_end[0]
        point_end_y = point_end[1]
        point_end_z = point_end[2]

        if point_start_z < height < point_end_z:
            intersect_points.append([point_start_x, point_start_y])

    x_range = sorted(set([i[0] for i in intersect_points]))
    vertical_order = True

    traverse_points = []
    for x in x_range:
        y_list = []
        for point in intersect_points:
            if point[0] == x:
                y_list.append(point[1])
        if vertical_order:
            y_list = sorted(y_list)
            vertical_order = False
        else:
            y_list = sorted(y_list, reverse = True)
            vertical_order = True
        for y in y_list:
            traverse_points.append([x, y]) 

    polylines = [[traverse_points[i],traverse_points[i+1]] for i in range(len(traverse_points)-1)]

    # import matplotlib.pyplot as plt
    # for i in polylines:
    #     ax = plt.axes()
    #     print(i[0][0])
    #     plt.plot(i[0][0], i[0][1], 'o')
    #     plt.plot(i[1][0], i[1][1], 'o')
    #     plt.show()

    return polylines

def get_support_polylines_list(mesh, sampling_distance, sliceplanes_height = []):

    BBox = mesh.bounding_box()
    slice_height_from = BBox.zmin
    slice_height_to = BBox.zmax

    slice_height_from += 0.198768976
    slice_height_to += 0.198768976
    normal = np.array([[0.],[0.],[1.]])

    if sliceplanes_height != []: # if empty
        sliceplanes_height = sliceplanes_height
        sliceplanes_height = np.array(sliceplanes_height)
    else:
        sliceplanes_height = np.arange(slice_height_from, slice_height_to, config.layerThickness)


    s, e = support_lines(mesh, sampling_distance)

    polylines = [arranged_polyline_from_support(s, e, height, config.layerThickness) for height in sliceplanes_height]
    return polylines

def visulisation(mesh, sampling_distance):
    bounding_box = our_mesh.bounding_box()
    bed_level = bounding_box.zmin


    cos_angle_threshold = -0.9
    support_required_mask = detect_support_requiring_facet(our_mesh, cos_angle_threshold, bed_level)
    groups = group_support_area(our_mesh, support_required_mask)
    support_points = sampling_support_points(our_mesh, support_required_mask, groups, sampling_distance)
    self_support_z_values = self_support_detection(mesh, bounding_box, support_points)

    ############# visulisation ####################
    from mpl_toolkits import mplot3d
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    # Create a new plot
    figure = plt.figure()
    axes = mplot3d.Axes3D(figure)

    # Load the STL files and add the vectors to the plot
    colors = ['r' if i else (0,1,0,0) for i in support_required_mask]

    # if len(support_required_mask) != 0: # if support_required_mask is not empty, change facet requiring support to be green
    #         for i in range(len(support_required_mask)):
    #             if support_required_mask[i]:
    #                 if colors[i] == 'r':
    #                     print('warning this facet requires support and self-supporting!!!!!!!')
    #                 else:
    #                     colors[i] = 'green'

    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.triangles, color=colors))

    # Auto scale to the mesh size
    scale = np.array([mesh.triangles[:,0], mesh.triangles[:,1], mesh.triangles[:,2]]).flatten(-1)
    axes.auto_scale_xyz(scale, scale, scale)

    # red_patch = mpatches.Patch(color='r', label='self-supporting facet')
    # green_patch = mpatches.Patch(color='green', label='support-require facet')
    # plt.legend(handles=[red_patch, green_patch])

    # for support_point in support_points:
    #     x = support_point[0]
    #     y = support_point[1]
    #     z = support_point[2]

    #     plt.plot([x,x],[y,y],[z-5,z+5])

    for support_point, self_support_z in zip(support_points, self_support_z_values):
        x = support_point[0]
        y = support_point[1]
        z = support_point[2]
        plt.plot([x,x],[y,y],[z,self_support_z])

    plt.show()

def main_slow():
    from stl import mesh as np_mesh
    import mesh_operations
    import numpy as np

    stl_mesh = np_mesh.Mesh.from_file("ps4.stl")
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True)
    # desending z ?
    our_mesh.sort_by_z(reverse=True)
    bounding_box = our_mesh.bounding_box()
    bed_level = bounding_box.zmin

    cos_angle_threshold = -0.9

    support_sampling_distance = 2
    support_polylines_list = get_support_polylines_list(our_mesh, support_sampling_distance)

def main_fast():

    from stl import mesh as np_mesh
    import mesh_operations
    import numpy as np

    stl_mesh = np_mesh.Mesh.from_file("ps4.stl")
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True)
    # desending z ?
    our_mesh.sort_by_z(reverse=True)
    bounding_box = our_mesh.bounding_box()
    bed_level = bounding_box.zmin

    cos_angle_threshold = -0.8
    support_sampling_distance = 2

    support_required_mask = detect_support_requiring_facet(our_mesh, cos_angle_threshold, bed_level)

    group_support_area(our_mesh, support_required_mask)


if __name__ == '__main__':
    main_fast()