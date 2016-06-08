import inspect, os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

import numpy as np
import slicer.config as config

############# function using for support generation #############
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

############# function using for support generation #############


class Support():
    """class for all the support logic"""
    def __init__(self, mesh):
        self.mesh = mesh
        self.mesh.bbox = mesh.bounding_box()
        self.mesh.min_x = mesh.min_x()
        self.mesh.max_x = mesh.max_x()
        self.mesh.min_y = mesh.min_y()
        self.mesh.max_y = mesh.max_y()
        self.mesh.min_z = mesh.min_z()
        self.mesh.max_z = mesh.max_z()
        self.mesh.bed_z = self.mesh.bbox.zmin
        self.support_required_mask = self.detect_support_requiring_facet()
        self.groups = self.group_support_area()
        

    def detect_support_requiring_facet(self):
        # threshold is cos(theta) value
        # if building_direction is vector [[0], [0], [1]]
        # if threshold is cos(-135 degree) = sqrt(2)/2 = -0.70710678118, means if angle is between 135 and 225 degree then these facet requres support
        normal_cos_theta = self.mesh.dot_building_direction()
        support_required_mask = (normal_cos_theta<config.supportOverhangangle) # boolean list indicating which triangle requires support 

        return support_required_mask  # returns a boolen list indicated which triangles require support

    def detect_support_requiring_facet(self, support_starts_height = 0.5):
        

        # threshold is cos(theta) value
        # if building_direction is vector [[0], [0], [1]]
        # if threshold is cos(-135 degree) = sqrt(2)/2 = -0.70710678118, means if angle is between 135 and 225 degree then these facet requres support
        normal_cos_theta = self.mesh.dot_building_direction()
        exceed_threshold_mask = (normal_cos_theta<config.supportOverhangangle) # boolean list indicating which triangle requires support 

        # also ignore the facet too close to the bed
        not_too_close_to_bed_mask = (self.mesh.max_z > self.mesh.bed_z + support_starts_height)
        support_required_mask = np.logical_and(exceed_threshold_mask, not_too_close_to_bed_mask)

        return support_required_mask # returns a boolen list indicated which triangles require support

    def group_support_area(self):

        import datetime
        start_time = datetime.datetime.now()

        support_triangles = self.mesh.triangles[self.support_required_mask]

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

        print('------- grouping time -------------')
        print(datetime.datetime.now() - start_time)

        # local_group_index based on the index of the suppport_mask to based on global index
        print(groups)
        global_support_index = [i for i, elem in enumerate(self.support_required_mask, 1) if elem]
        global_support_index = np.array(global_support_index)
        groups = [list(global_support_index[group]) for group in groups]
        print(len(groups))
        print(groups)
        raise Tiger
        return groups

    def group_support_area(self):

        import datetime
        start_time = datetime.datetime.now()

        support_triangles_index  = [i for i, elem in enumerate(self.support_required_mask, 1) if elem]

        triangle_index_and_its_neighbour = {}

        for tri_index in support_triangles_index:
            neighbour = set()
            triangle_index_and_its_neighbour[tri_index] = neighbour

            triangle = self.mesh.triangles[tri_index]
            x = list(triangle[0])
            y = list(triangle[1])
            z = list(triangle[2])

            for tri_detect_index in support_triangles_index:

                if tri_detect_index in triangle_index_and_its_neighbour and tri_index in triangle_index_and_its_neighbour[tri_detect_index]:
                    neighbour.add(tri_detect_index)
                    continue

                tri = self.mesh.triangles[tri_detect_index]

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

        print('------- grouping time -------------')
        print(datetime.datetime.now() - start_time)
        
        print(groups)
        return groups

    def sampling_support_points(self):

        support_points_by_group = []

        counter = 0 # debug
        for group in self.groups:
            counter += 1 # debug
            support_points = []
            support_points_by_group.append(support_points)

            group_tri = self.mesh.triangles[group]

            min_x = np.min(self.mesh.min_x[group])
            max_x = np.max(self.mesh.max_x[group])
            min_y = np.min(self.mesh.min_y[group])
            max_y = np.max(self.mesh.max_y[group])
            min_z = np.min(self.mesh.min_z[group])
            max_z = np.max(self.mesh.max_z[group])

            # sampling in x, y plane
            x_sample = np.arange(min_x, max_x, config.supportSamplingDistance)
            y_sample = np.arange(min_y, max_y, config.supportSamplingDistance)

            def ray_trace_mesh(ray, mesh):
                tri_index = 0
                for triangle in mesh:
                    res = ray_triangle_intersection(ray, triangle)
                    if res[0]:
                        return res[1] , tri_index # should only be one z value # index is for support only
                    tri_index += 1

            epsilon = 0.01
            for x in x_sample:
                for y in y_sample:
                    res = ray_trace_mesh([x, y, max_z + epsilon], group_tri)
                    if res != None:
                        z = res[0]
                        support_points.append([x, y, z])
                    else:
                        pass


        if len(self.groups) == 0:
            support_points_by_group = []
        else:
            pass

        return support_points_by_group

    def self_support_detection(self, support_points_by_groups):

        epsilon = 0.1

        ray_direction_vector = np.array([[0],[0],[-1]])

        bed_z = self.mesh.bed_z
        min_z_list = self.mesh.min_z
        min_x_list = self.mesh.min_x
        max_x_list = self.mesh.max_x
        min_y_list = self.mesh.min_y
        max_y_list = self.mesh.max_y

        z_triangle_selfsupport_by_groups = []

        for support_points in support_points_by_groups:

            z_triangle_selfsupport = [self.mesh.bed_z for i in range(len(support_points))]
            z_triangle_selfsupport_by_groups.append(z_triangle_selfsupport)

            for index in range(len(support_points)):
                x = support_points[index][0]
                y = support_points[index][1]
                z = support_points[index][2]

                mask_x = np.logical_and(max_x_list>x, min_x_list<x)
                mask_y = np.logical_and(max_y_list>y, min_y_list<y)
                mask_z = (min_z_list<z-epsilon)


                for tri_index in np.where(mask_z&mask_x&mask_y)[0]:
                    triangle = self.mesh.triangles[tri_index]
                    res = ray_triangle_intersection(support_points[index], triangle)
                    if res[0]:
                        if res[1] > z_triangle_selfsupport[index]:
                            z_triangle_selfsupport[index] = res[1]

        return z_triangle_selfsupport_by_groups   

    def support_lines(self):

        support_points_by_group = self.sampling_support_points()
        z_triangle_selfsupport_by_groups = self.self_support_detection(support_points_by_group)
        

        support_line_starts_list_by_group = []
        support_line_ends_list_by_group = []

        for support_points, self_support_z_values in zip(support_points_by_group, z_triangle_selfsupport_by_groups):

            support_line_starts_list = []
            support_line_ends_list = []
            support_line_starts_list_by_group.append(support_line_starts_list)
            support_line_ends_list_by_group.append(support_line_ends_list)

            for support_point, self_support_z in zip(support_points, self_support_z_values):
                x = support_point[0]
                y = support_point[1]
                z = support_point[2]
                support_line_starts_list.append([x, y, self_support_z])
                support_line_ends_list.append([x, y, z])

        return support_line_starts_list_by_group, support_line_ends_list_by_group

    def arranged_polyline_from_support(self, support_line_starts_list_by_group, support_line_ends_list_by_group, height, does_visualize = False):

        def vertical_line_intersect_horizontal_plane(line_start, line_end, plane_height):
            if line_start < plane_height < line_end:
                return True
            else:
                return False

        intersect_points_by_groups = []

        for support_line_starts_list, support_line_ends_list in zip(support_line_starts_list_by_group, support_line_ends_list_by_group):

            intersect_points = []
            intersect_points_by_groups.append(intersect_points)

            for point_start, point_end in zip(support_line_starts_list, support_line_ends_list):
                point_start_x = point_start[0]
                point_start_y = point_start[1]

                point_start_z = point_start[2]
                point_end_z = point_end[2]

                intersection = vertical_line_intersect_horizontal_plane(point_start_z, point_end_z, height)
                if intersection:
                    intersect_points.append([point_start_x, point_start_y])

        if does_visualize:
            import matplotlib.pyplot as plt
            from matplotlib import colors
            cname = iter(colors.cnames)
            for group in intersect_points_by_groups:
                c_n = next(cname)
                for point in group:
                    plt.plot(point[0], point[1], 'o', color = c_n)
            plt.show()

        # hack. to be improved on the polylines
        traverse_points_by_groups = []
        for intersect_points in intersect_points_by_groups:

            traverse_points = []
            traverse_points_by_groups.append(traverse_points)

            x_range = sorted(set([i[0] for i in intersect_points]))
            vertical_order = True
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
        polylines = []

        import numpy as np
        def distance_between_two_point(point_start, point_end):
            point_start = np.array(point_start)
            point_end = np.array(point_end)
            return np.linalg.norm(point_start - point_end)

        for traverse_points in traverse_points_by_groups:
            for i in range(len(traverse_points) - 1):
                point_start = traverse_points[i]
                point_end = traverse_points[i+1]
                if distance_between_two_point(point_start, point_end) < 2.1:
                    polylines += [[point_start, point_end]]
                else:
                    print('here')

        if does_visualize:
            import numpy as np
            import pylab as pl
            from matplotlib import collections  as mc

            lc = mc.LineCollection(polylines, linewidths=2)
            fig, ax = pl.subplots()
            ax.add_collection(lc)
            ax.autoscale()
            ax.margins(0.1)
            pl.show()

        return polylines

    def get_support_polylines_list(self, sliceplanes_height = []):

        BBox = self.mesh.bounding_box()
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

 
        s, e = self.support_lines()

        polylines = [self.arranged_polyline_from_support(s, e, height, False) for height in sliceplanes_height]
        return polylines

    def visulisation(self):
        support_points = self.sampling_support_points()
        self_support_z_values = self.self_support_detection(support_points)

        ############# visulisation ####################
        from mpl_toolkits import mplot3d
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        # Create a new plot
        figure = plt.figure()
        axes = mplot3d.Axes3D(figure)

        # Load the STL files and add the vectors to the plot

        from matplotlib import colors
        cname = iter(colors.cnames)

        colors = ['r' if i else (0,1,0,0.1) for i in self.support_required_mask]
        for group in self.groups:
            c_n = next(cname)
            for index in group:
                colors[index] = c_n


        # if len(self.support_required_mask) != 0: # if support_required_mask is not empty, change facet requiring support to be green
        #         for i in range(len(self.support_required_mask)):
        #             if self.support_required_mask[i]:
        #                 if colors[i] == 'r':
        #                     # print('warning this facet requires support and self-supporting!!!!!!!')
        #                     pass
        #                 else:
        #                     colors[i] = 'green'

        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.mesh.triangles, color=colors))
        # axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.triangles))
        # Auto scale to the mesh size
        scale = np.array([self.mesh.triangles[:,0], self.mesh.triangles[:,1], self.mesh.triangles[:,2]]).flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)

        red_patch = mpatches.Patch(color='r', label='self-supporting facet')
        green_patch = mpatches.Patch(color='green', label='support-require facet')
        plt.legend(handles=[red_patch, green_patch])

        support_points_by_groups = self.sampling_support_points()
        self_support_z_by_groups = self.self_support_detection(support_points)

        for support_points, self_support_z_values in zip(support_points_by_groups, self_support_z_by_groups):
            c_n = next(cname)
            for support_point, self_support_z in zip(support_points, self_support_z_values):
                print(self_support_z)
                x = support_point[0]
                y = support_point[1]
                z = support_point[2]
                plt.plot([x,x],[y,y],[z,self_support_z], color = c_n)

        plt.show()

def main():
    from stl import mesh as np_mesh
    import mesh_operations
    import numpy as np

    stl_mesh = np_mesh.Mesh.from_file("15_to_45_degree_overhang_test.stl")
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True)
    sup = Support(our_mesh)
    # a = sup.get_support_polylines_list()
    sup.get_support_polylines_list()
    # sup.visulisation()
if __name__ == '__main__':
    main()