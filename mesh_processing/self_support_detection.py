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

def update_mesh_by_desending_z(mesh):
    order = revert_sort_by_z(mesh)

    mesh.vectors = mesh.vectors[order]

    # IMPORTANT updating mesh after rotation
    # because the attributes are not updated by function rotate
    mesh.x = mesh.vectors[:,:,0]
    mesh.y = mesh.vectors[:,:,1]
    mesh.z = mesh.vectors[:,:,2]
    mesh.v0 = mesh.vectors[:, 0]
    mesh.v1 = mesh.vectors[:, 1]
    mesh.v2 = mesh.vectors[:, 2]
    mesh.update_normals() 
    mesh.update_areas() # update_areas depends on normals 
    mesh.update_min()

    return mesh

def triangle_center(stl_mesh):
    centers = (stl_mesh.v0 + stl_mesh.v1 + stl_mesh.v2)/3
    return centers

def min_z(mesh):
    return np.min(mesh.z, axis=1)

def min_x(mesh):
    return np.min(mesh.x, axis=1)

def max_x(mesh):
    return np.max(mesh.x, axis=1)

def min_y(mesh):
    return np.min(mesh.y, axis=1)

def max_y(mesh):
    return np.max(mesh.y, axis=1)

def boolist_for_support_requiring_facet(mesh, cos_angle_threshold):
    # threshold is cos(theta) value
    # if building_direction is vector [[0], [0], [1]]
    # if threshold is cos(-135 degree) = sqrt(2)/2 = -0.70710678118, means if angle is between 135 and 225 degree then these facet requres support

    normal_cos_theta = dot_building_direction(mesh)
    boolist_support_required = (normal_cos_theta<cos_angle_threshold) # boolean list indicating which triangle requires support 

    # also ignore the facet too close to the bed
    average_layer_thickness = 0.1 # configurate this
    bed_level = np.min(min_z(mesh))
    not_too_close_to_bed = (min_z(mesh) > bed_level + average_layer_thickness*3)

    boolist_support_required = np.logical_and(boolist_support_required, not_too_close_to_bed)

    return boolist_support_required # returns a boolen list indicated which triangles require support

def boolist_for_selfsupporting_facet(mesh, boolist_support_required):
    
    # assuming that the ray direction is [[0],[0],[-1]] and center of ray is center of facet
    # assuming ray direction is [[0],[0],[-1]] allows us using bounding box (min_x, max_x, min_y, max_y, min_z) 
    # of the facet requires support (the start of the ray, denote this facet to be startFacet) 
    # to minising the numbers of facet we need to check for intersection.
    # The following three condition are checked for minising the number of facet to check for ray intersection.
    # 1. facets' min z is smaller than min z of startFacet
    # 2. facets' interval (min x, max x) are intersecting with (min x, max x) of startFacet
    # 3. facets' interval (min y, max y) are intersecting with (min y, max y) of startFacet

    # Tiger P.S. if it's necessary this algorithm can be generalised to support any ray direction, 
    # the only thing need to be done is to rotate the points and proceed for these new x, y, z value.

    ray_direction_vector = np.array([[0],[0],[-1]])

    centers = triangle_center(mesh)
    bed_z = mesh.min_[2]
    min_z_list = min_z(mesh)
    min_x_list = min_x(mesh)
    max_x_list = max_x(mesh)
    min_y_list = min_y(mesh)
    max_y_list = max_y(mesh)

    boolist_triangle_selfsupport =  np.array([False for i in range(len(mesh.vectors))]) # a boolean array of false (0) 
    z_triangle_selfsupport = [bed_z for i in range(len(mesh.vectors))]

    for support_required_index in np.where(boolist_support_required)[0]:
        
        center = centers[support_required_index]
        min_z_value = min_z_list[support_required_index]
        min_x_value = min_x_list[support_required_index]
        min_y_value = min_y_list[support_required_index]
        max_x_value = max_x_list[support_required_index]
        max_y_value = max_y_list[support_required_index]

        mask_x = np.logical_not(np.logical_or(max_x_list<min_x_value, min_x_list>max_x_value))
        mask_y = np.logical_not(np.logical_or(max_y_list<min_y_value, min_y_list>max_y_value))
        mask_z = (min_z_list<min_z_value)
        
        for tri_index in np.where(mask_z&mask_x&mask_y)[0]:
            triangle = mesh.vectors[tri_index]
            if boolist_triangle_selfsupport[tri_index] is True: # this facet already needs for self-support
                break
            res = ray_triangle_intersection(center, triangle)
            if res[0]:
                boolist_triangle_selfsupport[tri_index] = True
                z_triangle_selfsupport[tri_index] = res[1]
                break #  when it finds the highest facet, don't need to search for lower facet (in terms of minimal z)

    # print(np.sum(boolist_triangle_selfsupport))
    # print(np.count_nonzero(z_triangle_selfsupport))
    return boolist_triangle_selfsupport, z_triangle_selfsupport

def boolist_for_selfsupporting_facet_modified_for_support_detection(mesh, boolist_support_required):
    
    # assuming that the ray direction is [[0],[0],[-1]] and center of ray is center of facet
    # assuming ray direction is [[0],[0],[-1]] allows us using bounding box (min_x, max_x, min_y, max_y, min_z) 
    # of the facet requires support (the start of the ray, denote this facet to be startFacet) 
    # to minising the numbers of facet we need to check for intersection.
    # The following three condition are checked for minising the number of facet to check for ray intersection.
    # 1. facets' min z is smaller than min z of startFacet
    # 2. facets' interval (min x, max x) are intersecting with (min x, max x) of startFacet
    # 3. facets' interval (min y, max y) are intersecting with (min y, max y) of startFacet

    # Tiger P.S. if it's necessary this algorithm can be generalised to support any ray direction, 
    # the only thing need to be done is to rotate the points and proceed for these new x, y, z value.

    ray_direction_vector = np.array([[0],[0],[-1]])

    centers = triangle_center(mesh)
    bed_z = mesh.min_[2]
    min_z_list = min_z(mesh)
    min_x_list = min_x(mesh)
    max_x_list = max_x(mesh)
    min_y_list = min_y(mesh)
    max_y_list = max_y(mesh)

    boolist_triangle_selfsupport =  np.array([False for i in range(len(mesh.vectors))]) # a boolean array of false (0) 
    z_triangle_selfsupport = [bed_z for i in range(len(mesh.vectors))]

    support_facet_and_self_support_facet_recroder = []
    for support_required_index in np.where(boolist_support_required)[0]:
        
        center = centers[support_required_index]
        min_z_value = min_z_list[support_required_index]
        min_x_value = min_x_list[support_required_index]
        min_y_value = min_y_list[support_required_index]
        max_x_value = max_x_list[support_required_index]
        max_y_value = max_y_list[support_required_index]

        mask_x = np.logical_not(np.logical_or(max_x_list<min_x_value, min_x_list>max_x_value))
        mask_y = np.logical_not(np.logical_or(max_y_list<min_y_value, min_y_list>max_y_value))
        mask_z = (min_z_list<min_z_value)
        
        for tri_index in np.where(mask_z&mask_x&mask_y)[0]:
            triangle = mesh.vectors[tri_index]
            if boolist_triangle_selfsupport[tri_index] is True: # this facet already needs for self-support
                support_facet_and_self_support_facet_recroder.append([support_required_index, tri_index])
                break
            res = ray_triangle_intersection(center, triangle)
            if res[0]:
                boolist_triangle_selfsupport[tri_index] = True
                z_triangle_selfsupport[tri_index] = res[1]
                support_facet_and_self_support_facet_recroder.append([support_required_index, tri_index])
                break #  when it finds the highest facet, don't need to search for lower facet (in terms of minimal z)

    return support_facet_and_self_support_facet_recroder

def visulisation_selfsupport_facet(mesh, boolist_triangle_selfsupport, boolist_support_required=[]):
    from mpl_toolkits import mplot3d
    from matplotlib import pyplot
    import matplotlib.patches as mpatches

    # Create a new plot
    figure = pyplot.figure()
    axes = mplot3d.Axes3D(figure)

    # Load the STL files and add the vectors to the plot
    colors = ['r' if i else 'b' for i in boolist_triangle_selfsupport]

    if len(boolist_support_required) != 0: # if boolist_support_required is not empty, change facet requiring support to be green
        for i in range(len(boolist_support_required)):
            if boolist_support_required[i]:
                if colors[i] == 'r':
                    # print('warning this facet requires support and self-supporting!!!!!!!')
                else:
                    colors[i] = 'green'

    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.vectors, color=colors))

    # Auto scale to the mesh size
    scale = mesh.points.flatten(-1)
    axes.auto_scale_xyz(scale, scale, scale)

    red_patch = mpatches.Patch(color='r', label='self-supporting facet')
    green_patch = mpatches.Patch(color='green', label='support-require facet')

    pyplot.legend(handles=[red_patch, green_patch])

    # Show the plot to the screen
    pyplot.show()

def areas_and_volumn_concerning_support(mesh):

    # make sure the mesh is updated if you rotate the mesh

    boolist_support_required = boolist_for_support_requiring_facet(mesh, cos_angle_threshold)
    boolist_triangle_selfsupport, z_triangle_selfsupport = boolist_for_selfsupporting_facet(mesh, boolist_support_required)

    # area for support
    total_area_support_facet = np.sum(mesh.areas[boolist_support_required])

    # area for self support
    total_area_self_support_facet = np.sum(mesh.areas[boolist_triangle_selfsupport])

    # reference volumn for support
    # volumn is calculated by multiple the length of supprt and the area of the facet requiring supprt
    centers = triangle_center(mesh)
    total_volumn_for_support_material = np.sum(np.absolute(mesh.areas.T[0] * (centers[:,2] - z_triangle_selfsupport)))

    return [total_area_support_facet, total_area_self_support_facet, total_volumn_for_support_material]

def update_mesh_by_desending_z(mesh):
    order = revert_sort_by_z(mesh)

    mesh.vectors = mesh.vectors[order]

    # IMPORTANT updating mesh after rotation
    # because the attributes are not updated by function rotate
    mesh.x = mesh.vectors[:,:,0]
    mesh.y = mesh.vectors[:,:,1]
    mesh.z = mesh.vectors[:,:,2]
    mesh.v0 = mesh.vectors[:, 0]
    mesh.v1 = mesh.vectors[:, 1]
    mesh.v2 = mesh.vectors[:, 2]
    mesh.update_normals() 
    mesh.update_areas() # update_areas depends on normals 
    mesh.update_min()

    return mesh

def simple_support_visualisation(mesh, boolist_support_required, boolist_triangle_selfsupport,  z_triangle_selfsupport):

    support_facet_and_self_support_facet_recroder = boolist_for_selfsupporting_facet_modified_for_support_detection(mesh, boolist_support_required)

    from mpl_toolkits import mplot3d
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    # Create a new plot
    figure = plt.figure()
    axes = mplot3d.Axes3D(figure)

    # Load the STL files and add the vectors to the plot
    colors = ['r' if i else (0,0,0,0) for i in boolist_triangle_selfsupport]

    if len(boolist_support_required) != 0: # if boolist_support_required is not empty, change facet requiring support to be green
        for i in range(len(boolist_support_required)):
            if boolist_support_required[i]:
                if colors[i] == 'r':
                    # print('warning this facet requires support and self-supporting!!!!!!!')
                else:
                    colors[i] = 'green'

    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.vectors, color=colors))

    # Auto scale to the mesh size
    scale = mesh.points.flatten(-1)
    axes.auto_scale_xyz(scale, scale, scale)

    red_patch = mpatches.Patch(color='r', label='self-supporting facet')
    green_patch = mpatches.Patch(color='green', label='support-require facet')

    plt.legend(handles=[red_patch, green_patch])


    ############# start of support visualisation #################

    # reference volumn for support
    # volumn is calculated by multiple the length of supprt and the area of the facet requiring supprt
    centers = triangle_center(mesh)
 
    # total_volumn_for_support_material = np.sum(np.absolute(mesh.areas.T[0] * (centers[:,2] - z_triangle_selfsupport)))

    # for support_facet_index_has_self_support, self_support_index in support_facet_and_self_support_facet_recroder:
    #     plt.plot([centers[support_facet_index_has_self_support][0],centers[support_facet_index_has_self_support][0]],
    #             [centers[support_facet_index_has_self_support][1],centers[support_facet_index_has_self_support][1]],
    #             [centers[support_facet_index_has_self_support][2],z_triangle_selfsupport[self_support_index]])

    # support_facet_index_has_self_support = [i[0] for i in support_facet_and_self_support_facet_recroder]

    # support_facet_index_no_self_support = set(np.where(boolist_support_required)[0]) - set(support_facet_index_has_self_support)

    # for support_facet_index_no_self in support_facet_index_no_self_support:
    #     plt.plot([centers[support_facet_index_no_self][0],centers[support_facet_index_no_self][0]],
    #             [centers[support_facet_index_no_self][1],centers[support_facet_index_no_self][1]],
    #             [centers[support_facet_index_no_self][2],mesh.min_[2]])

    ############# end of support visualisation #################

    # # Show the plot to the screen 
    # print('--------- facet require support ----------')
    # print(np.sum(boolist_support_required))
    groups_to_rectangle(mesh, boolist_support_required, z_triangle_selfsupport, support_area_detection(mesh, boolist_support_required ) )
    plt.show()

    return None

def support_area_detection(mesh, boolist_support_required = []):

    if boolist_support_required != []:
        support_triangles = mesh.vectors[boolist_support_required]
    else:
        support_triangles = mesh.vectors

    import datetime
    start_time = datetime.datetime.now()

    triangle_index_and_its_neighbour = {}
    for tri_index in range(len(support_triangles)):
        # print(tri_index)
        neighbour = set()
        triangle_index_and_its_neighbour[tri_index] = neighbour

        triangle = support_triangles[tri_index]
        x = list(triangle[0])
        y = list(triangle[1])
        z = list(triangle[2])

        for tri_detect_index in range(len(support_triangles)):

            tri = support_triangles[tri_detect_index]

            x_test = list(tri[0])
            y_test = list(tri[1])
            z_test = list(tri[2])

            if not np.array_equal([x,y,z], [x_test, y_test, z_test]): # make sure they are not the same
                # if np.allclose(x, x_test, atol=2) and np.allclose(y, y_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(x, x_test, atol=2) and np.allclose(y, z_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(x, y_test, atol=2) and np.allclose(y, z_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(x, x_test, atol=2) and np.allclose(z, y_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(x, x_test, atol=2) and np.allclose(z, z_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(x, y_test, atol=2) and np.allclose(z, z_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(y, x_test, atol=2) and np.allclose(z, y_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(y, x_test, atol=2) and np.allclose(z, z_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(y, y_test, atol=2) and np.allclose(z, z_test, atol=2):
                #     neighbour.add(tri_detect_index)
                #     continue

                if x == x_test:
                    neighbour.add(tri_detect_index)
                    continue
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


                # if np.allclose(x, x_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(x, y_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(x, z_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(y, x_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(y, y_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(y, z_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(z, x_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(z, y_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue
                # elif np.allclose(z, z_test, atol=0.01):
                #     neighbour.add(tri_detect_index)
                #     continue

            else:
                pass


    def dfs(graph, start):
        visited, stack = set(), [start]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                stack.extend(graph[vertex] - visited)
        return visited

    # try to group them together
    groups = []
    support_indexs = set(triangle_index_and_its_neighbour)
    while support_indexs:
        start = support_indexs.pop()
        group = []
        groups.append(group)

        visited = dfs(triangle_index_and_its_neighbour, start)
        for i in visited:
            group.append(i)
        support_indexs = support_indexs - visited

    # print('-------len of group-----------')
    # print(len(groups))

    # print('------- grouping time -------------')
    # print(datetime.datetime.now() - start_time)
    return groups

def groups_to_rectangle(mesh,boolist_support_required, z_triangle_selfsupport, groups = []):

    import matplotlib.pyplot as plt

    support_facet_and_self_support_facet_recroder = boolist_for_selfsupporting_facet_modified_for_support_detection(mesh, boolist_support_required)
    support_facet_and_self_support_facet_recroder = {i[0]:i[1] for i in support_facet_and_self_support_facet_recroder}

    triangles = mesh.vectors[boolist_support_required]
    group_triangles = []
    for group in groups:
        group_triangles.append([])
        for index in group:
            group_triangles[-1].append(triangles[index].tolist())

    for group_tri in group_triangles:
        group_0 = np.array(group_tri)

        min_x =  np.min(np.min(group_0[:,:,0]))
        max_x =  np.max(np.max(group_0[:,:,0]))
        min_y =  np.min(np.min(group_0[:,:,1]))
        max_y =  np.max(np.max(group_0[:,:,1]))
        min_z = np.min(np.min(group_0[:,:,2]))
        max_z = np.max(np.max(group_0[:,:,2]))

        # sampling in x, y plane
        sampling_distance = 3
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
                    z, triangle_index = res
                    index_without_support = np.where(boolist_support_required)[0][triangle_index]
                    if index_without_support in support_facet_and_self_support_facet_recroder:
                        self_support_index = support_facet_and_self_support_facet_recroder[index_without_support]
                        plt.plot([x,x],[y,y], [z, z_triangle_selfsupport[self_support_index]])
                    else:
                        plt.plot([x,x],[y,y], [z, -6.8])

                else:
                    pass

        for i in support_points:
            if i[2] == None:
                pass
            else:
                plt.plot([i[0],i[0]],[i[1],i[1]],[i[2], -6.8])

    return min_x, max_x, min_y, max_y, min_z, max_z


# if __name__ == '__main__':
#     from stl import mesh
#     import numpy as np
#     import datetime
#     stl_filepath = 'FLATFOOT_StanfordBunny_jmil_HIGH_RES_Smoothed.stl'

#     building_direction = np.array([[0],[0],[1]])
#     cos_angle_threshold = -0.70710678118 

#     random_rotation = [i*np.pi/10 for i in range(10)]

#     for rotation in random_rotation:
#         print('-----------------')
#         print(rotation)
#         start_time = datetime.datetime.now()
#         your_mesh = mesh.Mesh.from_file(stl_filepath, remove_empty_areas=True)
#         your_mesh.rotate([0.5, 0.5, 0.5], rotation) # rotate update vectors
#         your_mesh = update_mesh_by_desending_z(your_mesh)

#         total_area_support_facet, total_area_self_support_facet, total_volumn_for_support_material = areas_and_volumn_concerning_support(your_mesh)

#         print('area for support')
#         print(total_area_support_facet)
#         print('area for self support')
#         print(total_area_self_support_facet)
#         print('total volumn for support')
#         print(total_volumn_for_support_material)

#         print('--------time----------')
#         print(datetime.datetime.now()-start_time)

# uncomment the following and comment the above code up to "if __name__ == '__main__'" for a visulisation example
if __name__ == '__main__':
    from stl import mesh
    import numpy as np
    import datetime
    start_time = datetime.datetime.now()
    stl_filepath = 'elephant.stl'

    building_direction = np.array([[0],[0],[1]])
    cos_angle_threshold = -0.9

    your_mesh = mesh.Mesh.from_file(stl_filepath)
    your_mesh = update_mesh_by_desending_z(your_mesh)


    boolist_support_required = boolist_for_support_requiring_facet(your_mesh, cos_angle_threshold)
    boolist_triangle_selfsupport, z_triangle_selfsupport = boolist_for_selfsupporting_facet(your_mesh, boolist_support_required)      #     boolist_triangle_selfsupport, z_triangle_selfsupport = boolist_for_selfsupporting_facet(your_mesh, boolist_support_required)

    # visulisation_selfsupport_facet(your_mesh, boolist_triangle_selfsupport, boolist_support_required)

    # print('number support requrie facet')
    # print(np.sum(boolist_support_required))
    simple_support_visualisation(your_mesh, boolist_support_required, boolist_triangle_selfsupport, z_triangle_selfsupport)
    # groups_to_rectangle(your_mesh, boolist_support_required)


