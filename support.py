import inspect, os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

import numpy as np
import slicer.config as config
import slicer.clipper_operations as clipper_operations
from slicer.Polygon_stack import *
from slicer.Line_stack import *
from itertools import groupby
from collections import namedtuple

class group:
    pass

class SupportVerticallines:
    def __init__(self, svl_data_group):
        self.svl_data_group = svl_data_group
        self.reorder()
        self.line_x_y_group = self.get_x_y()
        
    def get_x_y(self):
        x_y = []
        for each_group in self.svl_data_group:
            x_y.append([])
            for each_svl_data in each_group:
                x_y[-1].append([each_svl_data.x, each_svl_data.y])
        return x_y

    def reorder(self):
        data = []
        
        for each_group in self.svl_data_group:
            data.append([])
            
            each_group = sorted(each_group, key = lambda d:d.x)

            groups = []
            flip_flop = 0
            for _, g in groupby(each_group, key = lambda d:d.x):
                groups.append(list(g))      # Store group iterator as a list

            for each_data in groups:
                flip_flop += 1
                if flip_flop % 2:
                    data[-1] += each_data
                else:
                    data[-1] += each_data[::-1]
        self.svl_data_group = data

    def index_list_intersect_with_plane(self, plane_height):

        def vertical_line_intersect_horizontal_plane(line_start, line_end, plane_height):
            if line_start < plane_height < line_end:
                return True
            else:
                return False
        
        sample_point_group = []
        for each_group in self.svl_data_group:
            sample_point_group.append([])
            for svl_data in each_group:
                if vertical_line_intersect_horizontal_plane(svl_data.z_start,
                                                            svl_data.z_end,
                                                            plane_height):
                    sample_point_group[-1].append([svl_data.x, svl_data.y])

        return sample_point_group # or mask

    def return_polylines(self, sampled_point):
        pl = Line_stack()
        for each_group in sampled_point:
            pl.new_line()
            
            for point_start_unscaled, point_end_unscaled in zip(each_group, each_group[1:]):


                point_start_scaled = pyclipper.scale_to_clipper(point_start_unscaled)
                point_end_scaled = pyclipper.scale_to_clipper(point_end_unscaled)

                # vertical, horizontal and line in 45 degree
                if np.sqrt((point_start_unscaled[0] - point_end_unscaled[0])**2 + (point_start_unscaled[1] - point_end_unscaled[1])**2 ) <= config.link_threshold: # new link line

                # if point_start_unscaled[0] == point_end_unscaled[0]: # only vertical line
                    pl.add_point_in_last_line(point_start_scaled)
                    pl.add_point_in_last_line(point_end_scaled)
                else: # point too far away
                    pl.new_line()
        pl.clean()
        return pl

        # pl.visualize_all()
    def return_polyline_by_height(self, plane_height, first_layer):
        sampled_point = self.index_list_intersect_with_plane(plane_height)
        ls = self.return_polylines(sampled_point)

        pyclipper_formatting = []
        
        # pyclipper_formatting += pl.offset(config.line_width)
        if first_layer:
            pyclipper_formatting += ls.offset_line(config.line_width)

        # pyclipper_formatting += pl.offset_point(0.2)
        # pyclipper_formatting += pl.offset_point(0.4)

        pyclipper_formatting = Polygon_stack(pyclipper_formatting)


        return [ls, pyclipper_formatting]
        

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
    point_start = np.array(point_start)
    point_end = np.array(point_end)
    return np.linalg.norm(point_start - point_end)

class Support:
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

    def group_support_area(self, closeThreshold = 2, large_triangle_area_threshold = 5):
        # group them together by connected group component algorithm 
        # from http://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/
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

        large_triangles_mask = self.mesh.areas.flatten()>large_triangle_area_threshold
        triangle_index_and_its_neighbour = {}

        for tri_index in support_triangles_index:

            neighbour = set()
            triangle_index_and_its_neighbour[tri_index] = neighbour

            triangle = self.mesh.triangles[tri_index]
            this_trangle_center = np.array([triangle[0]+triangle[1]+triangle[2]])/3
            # todo: think about the close limit on the next line

            # check with large triangles and the close (in terms of center distance) triangle to this triangle and 
            # see whether it is neighbour, check large triangles is because some triangle might not be close to this triangle
            # because one triangle is large so the centers will be far away
            close_triangles_mask = norm(centers - this_trangle_center, axis=1)<closeThreshold
            large_triangle_mask = large_triangles_mask[self.support_required_mask]
            test_triangle_mask = np.logical_or(close_triangles_mask, large_triangle_mask)

            # test_triangle_mask = close_triangles_mask
            test_index = support_triangles_index[test_triangle_mask]
            x = list(triangle[0])
            y = list(triangle[1])
            z = list(triangle[2])

            for tri_detect_index in test_index:

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

            neighbour.remove(tri_index) # itself

        print('------- grouping time -------------')
        print(datetime.datetime.now() - start_time)
        
        groups = connect_connected_component(triangle_index_and_its_neighbour)

        print('-------len of group-----------')
        print(len(groups))

        return groups

    def sampling_support_points(self): 
        '''
        by equal distance sampling point on the bounding box and raytrace these points onto the grouped area, 
        if it hits then take it as a support point
        '''

        offset = 0.5 

        import datetime
        start_time = datetime.datetime.now()

        support_points_by_groups = []

        for group in self.groups:
            support_points = []
            support_points_by_groups.append(support_points)

            group_tri = self.mesh.triangles[group]        

            min_x = np.min(self.mesh.min_x[group] + offset)
            max_x = np.max(self.mesh.max_x[group] - offset)
            min_y = np.min(self.mesh.min_y[group] + offset)
            max_y = np.max(self.mesh.max_y[group] - offset)
            min_z = np.min(self.mesh.min_z[group])
            max_z = np.max(self.mesh.max_z[group])

            # sampling in x, y plane
            x_sample = list(np.arange(min_x, max_x, config.supportSamplingDistance))
            # if the sampling end point is too far from the offseted end point add the offseted end point
            if len(x_sample) > 0 and max_x - x_sample[-1] > offset:
                x_sample.append(max_x)
            y_sample = list(np.arange(min_y, max_y, config.supportSamplingDistance))
            # if the sampling end point is too far from the offseted end point add the offseted end point
            if len(y_sample) > 0 and max_y - y_sample[-1] > offset:
                y_sample.append(max_y)

            epsilon = 0.3
            for x in x_sample:
                for y in y_sample:
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

        print('time for sampling support point')
        print(datetime.datetime.now() - start_time)
        self.support_points_by_groups = support_points_by_groups

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
        Support_Vertical_Line_Data = namedtuple('Support_Vertical_Line_Data', 'x y z_start z_end')
        Support_Vertical_Line_Data_group = []

        self.sampling_support_points()

        z_triangle_selfsupport_by_groups = self.self_support_detection(self.support_points_by_groups)
        
        for support_points, self_support_z_values in zip(self.support_points_by_groups, z_triangle_selfsupport_by_groups):
            Support_Vertical_Line_Data_group.append([])

            for support_point, self_support_z in zip(support_points, self_support_z_values):
                x = support_point[0]
                y = support_point[1]
                z = support_point[2]
                z_start = self_support_z
                z_end = z

                Support_Vertical_Line_Data_group[-1].append(Support_Vertical_Line_Data(x, y, z_start, z_end))

        svl = SupportVerticallines(Support_Vertical_Line_Data_group)

        return svl

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
            self.sampling_support_points()
            self.support_lines()
            self_support_z_by_groups = self.self_support_detection(self.support_points_by_groups)

            for support_points, self_support_z_values in zip(self.support_points_by_groups, self_support_z_by_groups):
                if len(self_support_z_by_groups) > 50:
                    c_n = 'r'
                else:
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

        svl = self.support_lines()

        polylines_all = []
        layer_counter = 0
        for height in sliceplanes_height:
            if layer_counter <= 1:
                polylines_all.append(svl.return_polyline_by_height(height, True))
            else:
                polylines_all.append(svl.return_polyline_by_height(height, False))
            layer_counter += 1

        return polylines_all

def main():
    from stl import mesh as np_mesh
    import mesh_operations
    import numpy as np
    import datetime
    import slicer.config as config
    config.reset()
    start_time = datetime.datetime.now()
    mesh_name = "overhang_test_stl/SupportTEST.stl"
    stl_mesh = np_mesh.Mesh.from_file(mesh_name)
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True)
    sup = Support(our_mesh)
    sup.visulisation(require_support_lines=True)

if __name__ == '__main__':
    main()