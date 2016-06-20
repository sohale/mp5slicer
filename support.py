import inspect, os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

import numpy as np
import slicer.config as config
import slicer.clipper_operations as clipper_operations

class PolyLines: # using pyclipper paths format
    def __init__(self):
        self.line_points = []
    def __len__(self):
        return len(sampling_points_by_groups)
    def add_point_chain(self, points):
        self.new_line()
        self.line_points[-1] += points
    def new_line(self):
        self.line_points.append([])
    def add_point_in_last_line(self, point):
        if self.line_points[-1] == []:
            self.line_points[-1].append(point)
        elif self.line_points[-1][-1] == point:
            pass
        else:
            self.line_points[-1].append(point)
    def add_point_in_new_line(self, point):
        self.line_points.append([point])
    def return_polylines(self):
        polylines = []
        if self.non_empty():
            for each_line in self.line_points:
                polylines += zip(each_line, each_line[1:])
        return polylines
    def offset(self, offset_value, point=False):

        if point: # hack
            points = []
            for each_line in self.line_points:
                if len(each_line) == 1:
                    points.append(each_line)

            sol = clipper_operations.LinesOffset(points, offset_value+0.2)
            for each_line_index in range(len(sol)): 
                sol[each_line_index].append(sol[each_line_index][0])

            return sol

        sol = clipper_operations.LinesOffset(self.line_points, offset_value)
        
        # extra offset for points 
        points = []
        for each_line in self.line_points:
            if len(each_line) == 1:
                points.append(each_line)

        sol += clipper_operations.LinesOffset(points, offset_value+0.2)

        for each_line_index in range(len(sol)): 
            sol[each_line_index].append(sol[each_line_index][0])

        return sol
    def non_empty(self):
        if self.line_points != []:
            return True
        else:
            return False
    def visualize_all(self):
        import matplotlib.pyplot as plt
        for each_line in self.line_points:
            x = [i[0] for i in each_line]
            y = [i[1] for i in each_line]
            if len(x) == 1:
                plt.plot(x,y,'o')
            else:
                plt.plot(x,y,'-')

        plt.show()
    def visualize_last_line(self):
        x = [i[0] for i in self.line_points[-1]]
        y = [i[1] for i in self.line_points[-1]]

        import matplotlib.pyplot as plt
        plt.plot(x,y,'b-')
        plt.show()
    
    def __len__(self):
        return len(self.line_points)


class SupportSamplingPoint:
    def __init__(self, sampling_points_by_groups):
        assert(isinstance(sampling_points_by_groups, dict))
        self.sampling_points_by_groups = sampling_points_by_groups
        self.group_index = list(self.sampling_points_by_groups)

    def __len__(self):
        return sum([len(self.sampling_points_by_groups[i]) for i in self.sampling_points_by_groups])

    def reorder_sampling_points(self):
        ############### ordering traverse points ###############
        for group_index in list(self.sampling_points_by_groups):

            points_in_each_group = self.sampling_points_by_groups[group_index]
            ordered_traverse_points = []

            # sorting first by x then by y, the value of y flip by each change of x

            x_range = sorted(set([i[0] for i in points_in_each_group]))
            vertical_order = True
            for x in x_range:
                y_list = []
                for point in points_in_each_group:
                    if point[0] == x:
                        y_list.append(point[1])
                if vertical_order:
                    y_list = sorted(y_list)
                    vertical_order = False
                else:
                    y_list = sorted(y_list, reverse = True)
                    vertical_order = True
                for y in y_list:
                    ordered_traverse_points.append([x, y]) 

            self.sampling_points_by_groups[group_index] = ordered_traverse_points

    def visulisation(self):
        import matplotlib.pyplot as plt
        from matplotlib import colors
        cname = iter(colors.cnames)
        for group_index in list(self.group_index):
            c_n = next(cname)
            for point in self.sampling_points_by_groups[group_index]:
                plt.plot(point[0], point[1], 'o', color = c_n)
        plt.show()

    def polyline_generation(self, does_visualize = False):
        import numpy as np
        # reorder the points
        self.reorder_sampling_points()
                ################# polylines generation

        pl = PolyLines()
        # for traverse_points in traverse_points_by_groups:
        for group_index in self.group_index:

            points_added = set()
            pl.new_line()

            points_in_this_group = self.sampling_points_by_groups[group_index]
            for i in range(len(self.sampling_points_by_groups[group_index]) - 1):
                point_start = points_in_this_group[i]
                point_end = points_in_this_group[i+1]
                if distance_between_two_point(point_start, point_end) <=  np.sqrt(2*(config.supportSamplingDistance**2)):
                    # polylines_connected[-1].append([point_start, point_end]) # coneected polylines
                    pl.add_point_in_last_line(point_start)
                    pl.add_point_in_last_line(point_end)
                    points_added.add(i) # testing
                    points_added.add(i+1) # testing
                else:
                    if does_visualize: # visualize each connected line
                        pl.visualize_last_line()
                    pl.new_line()

            single_point_sup = set(range(len(points_in_this_group))).difference(points_added) # points added
            single_point_sup = list(single_point_sup)

            while single_point_sup:

                single_point_index = single_point_sup.pop()
                # try to linked to a close point within the same group
                single_point = list(points_in_this_group[single_point_index])

                single_connected = False
                for point_added_index in list(points_added):
                    test_point = list(points_in_this_group[point_added_index])
                    if distance_between_two_point(single_point, test_point) <=  np.sqrt(2*(config.supportSamplingDistance**2)):
                        # polylines_connected.append([single_point,test_point])
                        pl.add_point_chain([single_point,test_point])
                        # print(polylines_connected[-1])

                        single_connected = True
                        break

                if single_connected:
                    pass
                else:
                    pl.add_point_in_new_line(single_point)

        return pl


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

def ray_trace_mesh(ray, mesh):
    tri_index = 0
    for triangle in mesh:
        res = ray_triangle_intersection(ray, triangle)
        if res[0]:
            return res[1] , tri_index # should only be one z value # index is for support only
        else:
            pass
        tri_index += 1

def get_center(mesh_triangles):
    return (mesh_triangles[:,0] + mesh_triangles[:,1] + mesh_triangles[:,2])/3

def distance_between_two_point(point_start, point_end):
    import numpy as np
    point_start = np.array(point_start)
    point_end = np.array(point_end)
    return np.linalg.norm(point_start - point_end)

class Support():
    """class for all the support logic"""
    def __init__(self, mesh):
        self.mesh = mesh
        self.mesh.bbox = mesh.bounding_box()
        self.mesh.min_x = mesh.min_x() # numpy array
        self.mesh.max_x = mesh.max_x() # numpy array
        self.mesh.min_y = mesh.min_y() # numpy array
        self.mesh.max_y = mesh.max_y() # numpy array
        self.mesh.min_z = mesh.min_z() # numpy array
        self.mesh.max_z = mesh.max_z() # numpy array
        self.mesh.bed_z = self.mesh.bbox.zmin
        self.support_required_mask = self.detect_support_requiring_facet()
        self.groups = self.group_support_area()

    def detect_support_requiring_facet(self, support_starts_height = 0.1):
        

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

        def connect_connected_component(graph):
            def dfs(graph, start):
                visited, stack = set(), [start]
                while stack:
                    vertex = stack.pop()
                    if vertex not in visited:
                        visited.add(vertex)
                        stack.extend(graph[vertex] - visited)
                return visited

            groups = []
            support_indexs = set(graph)
            while support_indexs:
                start = support_indexs.pop()
                visited = dfs(graph, start)
                group = list(visited)
                groups.append(group)
                support_indexs = support_indexs - visited
            return groups

        import datetime
        from numpy.linalg import norm
        start_time = datetime.datetime.now()

        ## use global index 
        support_triangles_index  = np.where(self.support_required_mask)[0]
        centers = get_center(self.mesh.triangles[support_triangles_index])

        triangle_index_and_its_neighbour = {}

        for tri_index in support_triangles_index:
            neighbour = set()
            triangle_index_and_its_neighbour[tri_index] = neighbour

            triangle = self.mesh.triangles[tri_index]
            this_trangle_center = np.array([triangle[0]+triangle[1]+triangle[2]])/3


            # if center within sampling distance check whether they are next to each other
            # todo: think about the close limit on the next line
            close_triangles_index = support_triangles_index[norm(centers - this_trangle_center, axis=1)<config.supportSamplingDistance]
            # need to think about how to deal with large area triangles
            # now the triangle with large area will be in its own group

            x = list(triangle[0])
            y = list(triangle[1])
            z = list(triangle[2])

            for tri_detect_index in close_triangles_index:

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

        print('------- grouping time -------------')
        print(datetime.datetime.now() - start_time)
        
        groups = connect_connected_component(triangle_index_and_its_neighbour)

        print('-------len of group-----------')
        print(len(groups))

        return groups

    def sampling_support_points(self, offset_boundingbox = config.layerThickness): 
        '''
        by equal distance sampling point on the bounding box and raytrace these points onto the grouped area, 
        if it hits then take it as a support point
        '''

        import datetime
        start_time = datetime.datetime.now()

        support_points_by_group = []

        for group in self.groups:
            support_points = []
            support_points_by_group.append(support_points)

            group_tri = self.mesh.triangles[group]        

            min_x = np.min(self.mesh.min_x[group] + offset_boundingbox)
            max_x = np.max(self.mesh.max_x[group] - offset_boundingbox)
            min_y = np.min(self.mesh.min_y[group] + offset_boundingbox)
            max_y = np.max(self.mesh.max_y[group] - offset_boundingbox)
            min_z = np.min(self.mesh.min_z[group] + offset_boundingbox)
            max_z = np.max(self.mesh.max_z[group] - offset_boundingbox)

            # sampling in x, y plane
            x_sample = np.arange(min_x, max_x, config.supportSamplingDistance)
            y_sample = np.arange(min_y, max_y, config.supportSamplingDistance)

            epsilon = 0.3
            for x in x_sample:
                for y in y_sample:
                    down_sampling_ray_trace_triangle_mask = np.logical_and(min_x <= x <= max_x, 
                                                                           min_y <= y <= max_y)
                    x_mask = np.logical_and(self.mesh.min_x[group] <= x, x <= self.mesh.max_x[group])
                    y_mask = np.logical_and(self.mesh.min_y[group] <= y, y <= self.mesh.max_y[group])
                    all_mask = np.logical_and(x_mask, y_mask)
                    
                    ray_trace_tri = group_tri[all_mask]
                    res = ray_trace_mesh([x, y, max_z + epsilon], ray_trace_tri)
                    if res != None:
                        z = res[0]
                        support_points.append([x, y, z])
                    else:
                        pass


        if len(self.groups) == 0:
            support_points_by_group = []
        else:
            pass

        print('time for sampling support point')
        print(datetime.datetime.now() - start_time)
        return support_points_by_group

    def self_support_detection(self, support_points_by_groups):

        import datetime
        start_time = datetime.datetime.now()

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

        print('time for self-detection')
        print(datetime.datetime.now() - start_time)
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

    def arranged_polyline_from_support(self, support_line_starts_list_by_group, support_line_ends_list_by_group, height, does_visualize = False, first_layer=False):
        def vertical_line_intersect_horizontal_plane(line_start, line_end, plane_height):
            if line_start < plane_height < line_end:
                return True
            else:
                return False

        ######################### point sampling for layer #########################
        intersect_points_by_groups = {}
        group_index = 0
        for support_line_starts_list, support_line_ends_list in zip(support_line_starts_list_by_group, support_line_ends_list_by_group):

            intersect_points = []
            intersect_points_by_groups[group_index] = intersect_points

            for point_start, point_end in zip(support_line_starts_list, support_line_ends_list):
                point_start_x = point_start[0]
                point_start_y = point_start[1]

                point_start_z = point_start[2]
                point_end_z = point_end[2]

                intersection = vertical_line_intersect_horizontal_plane(point_start_z, point_end_z, height)
                if intersection:
                    intersect_points.append([point_start_x, point_start_y])

            group_index += 1

        sample_point = SupportSamplingPoint(intersect_points_by_groups)
        pl = sample_point.polyline_generation(does_visualize=False)


        polylines = []
        polylines += pl.return_polylines()
        polylines += pl.offset(0.2, point=True) # offset point
        polylines += pl.offset(0.4, point=True) # offset point
        if first_layer:
            polylines += pl.offset(0.2)
            polylines += pl.offset(0.4)
            polylines += pl.offset(0.6)
            polylines += pl.offset(0.8)
            polylines += pl.offset(1.0)

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

    def visulisation(self, require_group = False, require_support_lines = False):

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

        colors = [(0,1,0,0.1) for i in range(len(self.mesh.triangles))]
        for index in np.where(self.support_required_mask)[0]:
            colors[index] = 'r'

        if require_group:
            for group in self.groups:
                c_n = next(cname)
                for index in group:
                    colors[index] = c_n

        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.mesh.triangles, color=colors))
        # Auto scale to the mesh size
        scale = np.array([self.mesh.triangles[:,0], self.mesh.triangles[:,1], self.mesh.triangles[:,2]]).flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)

        if require_support_lines:
            support_points_by_groups = self.sampling_support_points()
            self_support_z_by_groups = self.self_support_detection(support_points_by_groups)

            for support_points, self_support_z_values in zip(support_points_by_groups, self_support_z_by_groups):
                c_n = next(cname)
                for support_point, self_support_z in zip(support_points, self_support_z_values):
                    x = support_point[0]
                    y = support_point[1]
                    z = support_point[2]
                    plt.plot([x,x],[y,y],[z,self_support_z], color = c_n)

        plt.show()

    def get_support_polylines_list(self):

        BBox = self.mesh.bounding_box()
        slice_height_from=BBox.zmin
        slice_height_to=BBox.zmax
        slice_step= config.layerThickness

        slice_height_from += 0.198768976
        slice_height_to += 0.198768976
        normal = np.array([[0.],[0.],[1.]])

        sliceplanes_height = np.arange(slice_height_from, slice_height_to, slice_step)

        s,e = self.support_lines()
        polylines_all = []

        layer_count = 0
        for height in sliceplanes_height:
            if layer_count <= 5:
                polylines_all += [self.arranged_polyline_from_support(s, e, height, first_layer=True)]
                # print('first layer')
            else:
                polylines_all += [self.arranged_polyline_from_support(s, e, height)]
            layer_count += 1
        return polylines_all

def main():
    from stl import mesh as np_mesh
    import mesh_operations
    import numpy as np

    import datetime
    start_time = datetime.datetime.now()
    mesh_name = "bunny_0.7.stl"
    stl_mesh = np_mesh.Mesh.from_file(mesh_name)
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True)
    sup = Support(our_mesh)
    # s,e = sup.support_lines()
    # sup.arranged_polyline_from_support(s,e,1,does_visualize=False,first_layer=False)
    # sup.visulisation(require_support_lines=True)

    sup.get_support_polylines_list()

if __name__ == '__main__':
    main()