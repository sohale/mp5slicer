'''
This file is for support algorithms.
'''

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
    triangle_index_and_its_neighbour = {}

    for tri_index in range(len(support_triangles)):
        neighbour = set()
        triangle_index_and_its_neighbour[tri_index] = neighbour

        triangle = support_triangles[tri_index]
        x = list(triangle[0])
        y = list(triangle[1])
        z = list(triangle[2])

        for tri_detect_index in range(len(support_triangles)):

            if not tri_detect_index == tri_index: # if not same triangle
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

    print('------- grouping time -------------')
    print(datetime.datetime.now() - start_time)
    return groups



def sampling_support_points(mesh, support_required_mask, groups):

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
        sampling_distance = 2
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

    return support_points

def self_support_detection(mesh, bounding_box, support_points):

    epsilon = 0.1

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

    ray_direction_vector = np.array([[0],[0],[-1]])

    bed_z = bounding_box.zmin
    min_z_list = min_z(mesh)
    min_x_list = min_x(mesh)
    max_x_list = max_x(mesh)
    min_y_list = min_y(mesh)
    max_y_list = max_y(mesh)

    boolist_triangle_selfsupport =  np.array([False for i in range(len(mesh.triangles))]) # a boolean array of false (0) 
    z_triangle_selfsupport = [bed_z for i in range(len(mesh.triangles))]

    for support_point in support_points:
        x = support_point[0]
        y = support_point[1]
        z = support_point[2]

        mask_x = np.logical_not(np.logical_or(max_x_list< x-epsilon, min_x_list>x+epsilon))
        mask_y = np.logical_not(np.logical_or(max_y_list< y-epsilon, min_y_list>y+epsilon))
        mask_z = (min_z_list<z-epsilon)


        for tri_index in np.where(mask_z&mask_x&mask_y)[0]:
            triangle = mesh.triangles[tri_index]
            if boolist_triangle_selfsupport[tri_index] is True: # this facet already needs for self-support
                break
            res = ray_triangle_intersection(support_point, triangle)
            if res[0]:
                boolist_triangle_selfsupport[tri_index] = True
                z_triangle_selfsupport[tri_index] = res[1]
                break #  when it finds the highest facet, don't need to search for lower facet (in terms of minimal z)

    return boolist_triangle_selfsupport, z_triangle_selfsupport

def visulisation(mesh):
    bounding_box = our_mesh.bounding_box()
    bed_level = bounding_box.zmin

    cos_angle_threshold = -0.9
    support_required_mask = detect_support_requiring_facet(our_mesh, cos_angle_threshold, bed_level)
    groups = group_support_area(our_mesh, support_required_mask)
    support_points = sampling_support_points(our_mesh, support_required_mask, groups)
    self_support_mask, self_support_z_values = self_support_detection(mesh, bounding_box, support_points)

    ############# visulisation ####################
    from mpl_toolkits import mplot3d
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    # Create a new plot
    figure = plt.figure()
    axes = mplot3d.Axes3D(figure)

    # Load the STL files and add the vectors to the plot
    colors = ['r' if i else (0,1,0,0) for i in self_support_mask]

    if len(support_required_mask) != 0: # if support_required_mask is not empty, change facet requiring support to be green
            for i in range(len(support_required_mask)):
                if support_required_mask[i]:
                    if colors[i] == 'r':
                        print('warning this facet requires support and self-supporting!!!!!!!')
                    else:
                        colors[i] = 'green'

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

    self_support_z_values = np.array(self_support_z_values)[self_support_mask]
    for support_point, self_support_z in zip(support_points, self_support_z_values):
        x = support_point[0]
        y = support_point[1]
        z = support_point[2]
        plt.plot([x,x],[y,y],[z,self_support_z])

    plt.show()

if __name__ == '__main__':
    from stl import mesh as np_mesh
    import mesh_operations
    import numpy as np

    stl_mesh = np_mesh.Mesh.from_file("elephant.stl")
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True)
    # desending z ?
    our_mesh.sort_by_z(reverse=True)
    bounding_box = our_mesh.bounding_box()
    bed_level = bounding_box.zmin

    cos_angle_threshold = -0.9

    support_required_mask = detect_support_requiring_facet(our_mesh, cos_angle_threshold, bed_level)
    groups = group_support_area(our_mesh, support_required_mask)
    support_points = sampling_support_points(our_mesh, support_required_mask, groups)

    self_support_detection(our_mesh, bounding_box, support_points)

    visulisation(our_mesh)