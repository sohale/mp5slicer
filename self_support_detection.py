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

def ray_triangle_intersection_old(ray_near, triangle):
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
    pvec = np.cross(ray_dir, edge2)
    det = edge1.dot(pvec)
    if abs(det) < eps:
        return False, None
    inv_det = 1. / det
    tvec = ray_near - v1
    u = tvec.dot(pvec) * inv_det
    if u < 0. or u > 1.:
        return False, None
    qvec = np.cross(tvec, edge1)
    v = ray_dir.dot(qvec) * inv_det
    if v < 0. or u + v > 1.:
        return False, None
    t = edge2.dot(qvec) * inv_det
    if t < eps:
        return False, None

    point = ray_near + ray_dir*t
    z_value = point[2]

    return True, z_value

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
        
        for tri_index in np.where(mask_x&mask_y&mask_z)[0]:
            triangle = mesh.vectors[tri_index]
            if boolist_triangle_selfsupport[tri_index] is True: # this facet already needs for self-support
                break
            res = ray_triangle_intersection(center, triangle)
            if res[0]:
                boolist_triangle_selfsupport[tri_index] = True
                z_triangle_selfsupport[tri_index] = res[1]
                break #  when it finds the highest facet, don't need to search for lower facet (in terms of minimal z)

    return boolist_triangle_selfsupport, z_triangle_selfsupport

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
                    print('warning this facet requires support and self-supporting!!!!!!!')
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

if __name__ == '__main__':
    from stl import mesh
    import numpy as np
    import datetime
    stl_filepath = 'FLATFOOT_StanfordBunny_jmil_HIGH_RES_Smoothed.stl'

    building_direction = np.array([[0],[0],[1]])
    cos_angle_threshold = -0.70710678118 

    random_rotation = [i*np.pi/10 for i in range(1)]

    for rotation in random_rotation:
        print('-----------------')
        print(rotation)
        start_time = datetime.datetime.now()
        your_mesh = mesh.Mesh.from_file(stl_filepath)
        your_mesh.rotate([0.5, 0.5, 0.5], rotation) # rotate update vectors
        your_mesh = update_mesh_by_desending_z(your_mesh)

        total_area_support_facet, total_area_self_support_facet, total_volumn_for_support_material = areas_and_volumn_concerning_support(your_mesh)

        print('area for support')
        print(total_area_support_facet)
        print('area for self support')
        print(total_area_self_support_facet)
        print('total volumn for support')
        print(total_volumn_for_support_material)

        print('--------time----------')
        print(datetime.datetime.now()-start_time)

# uncomment the following and comment the above code up to "if __name__ == '__main__'" for a visulisation example
# if __name__ == '__main__':
#     from stl import mesh
#     import numpy as np
#     import datetime
#     stl_filepath = 'raytracingtest.stl'

#     building_direction = np.array([[0],[0],[1]])
#     cos_angle_threshold = -0.70710678118 

#     your_mesh = mesh.Mesh.from_file(stl_filepath)

#     your_mesh = update_mesh_by_desending_z(your_mesh) # this step is for optimising selfsupport raytracing calculation

#     boolist_support_required = boolist_for_support_requiring_facet(your_mesh, building_direction, cos_angle_threshold)
#     boolist_triangle_selfsupport, z_triangle_selfsupport = boolist_for_selfsupporting_facet(your_mesh, boolist_support_required)
#     visulisation_selfsupport_facet(your_mesh, boolist_triangle_selfsupport, boolist_support_required)


