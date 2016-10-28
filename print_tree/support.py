import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

import numpy as np
import mp5slicer.config.config as config
from mp5slicer.print_tree.Polygon_stack import *
from mp5slicer.print_tree.Line_stack import SupportLineStack
from itertools import groupby
from collections import namedtuple
from mp5slicer.commons.utils import scale_point_to_clipper, scale_point_from_clipper
from mp5slicer.commons.utils import distance as calulate_distance


############################## support by mesh ##############################
def ray_triangle_intersection(ray_near, triangle):
    """
    Taken from Printrun
    Moller-Trumbore intersection algorithm in pure python
    Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    ray_dir is set as [[0],[0],[-1]] for optimizing running speed
    ray_near should be the origin of this ray.
    """
    v1, v2, v3 = triangle # vertices are in 3d

    ray_dir = np.asarray([0, 0, -1])  # column vector to row vector
    
    eps = 0.000001
    edge1 = v2 - v1
    edge2 = v3 - v1
    pvec = [edge2[1], -edge2[0], 0]  # pvec = np.cross(ray_dir, edge2)
    det = edge1[0]*pvec[0] + edge1[1]*pvec[1]  # det = edge1.dot(pvec)
    if abs(det) < eps:
        return False, None
    inv_det = 1. / det
    tvec = ray_near - v1
    u = (tvec[0]*pvec[0]+tvec[1]*pvec[1]) * inv_det  # u = tvec.dot(pvec) * inv_det
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
#     Moller-Trumbore intersection algorithm in pure python
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
    for triangle_index in range(len(mesh)):
        triangle = mesh[triangle_index]
        does_intersect, intersect_z_value = ray_triangle_intersection(ray, triangle)
        if does_intersect:
            # should only be one z value # index is for support only
            return intersect_z_value, triangle_index
        else:
            pass

def get_center(mesh_triangles):
    return (mesh_triangles[:,0] + mesh_triangles[:,1] + mesh_triangles[:,2])/3

class Last_point(object):
    def __init__(self, point):
        self.point = point  # [x, y]
    def return_point_as_new_line(self):  # pyclipper formatting
        return [self.point]
    @staticmethod
    def offset_value():
        return 0 # one empty layer
        # return 0.1


class Support_Vertical_lines(object):
    def __init__(self):
        '''
        group is for grouping connected supported require area,

        ===|===
         A | B
           |
        
        For example, the above object made by equal sign and verticle has two areas
        which require support, they will be seperated into two groups.
        so the self.svl_data_group will look like [[A], [B]], where A, B are the triangles 
        which define the support require area.

        '''
        self.svl_data_group = [] 

    def __iter__(self):
        return iter(self.svl_data_group)

    def __len__(self):
        return len(self.svl_data_group)

    def add_support_point():
        pass
    def add_support_group():
        pass

    def apply_function_on_group(self, function):
        return list(map(function, self.svl_data_group))

    # def clean(self):
    #     ''' remove the short svls which will only be printed on x number of layer'''
    #     def clean_each_group(each_svl_data_group):
    #         element_counter = 0
    #         while element_counter < len(each_svl_data_group):
    #             each_svl_data = each_svl_data_group[element_counter]
        
    #             if each_svl_data.z_low <= 2*config.LAYER_THICHNESS:
    #                 element_counter += 1
    #             else:
    #                 if each_svl_data.z_high - each_svl_data.z_low <= 2*config.LAYER_THICHNESS:
    #                     print("deleted one")
    #                     print(each_svl_data)
    #                     del each_svl_data_group[element_counter]  
    #                 else:
    #                     element_counter += 1

    #     self.apply_function_on_group(clean_each_group)

    def append_group(self):
        self.svl_data_group.append([])

    def append_svl_data_to_last_group(self, svl_data):
        assert isinstance(svl_data, Support_Vertical_lines.Support_Vertical_Line_Data)
        assert len(self.svl_data_group) != 0
        self.svl_data_group[-1].append(svl_data)

    def add_sliceplanes_height(self, sliceplanes_height):
        self.sliceplanes_height = sliceplanes_height

    def get_last_layer(self):
        def get_last_layer_each_group(each_svl_data_group):
            for each_svl in each_svl_data_group:
                for height_from, height_to in zip(self.sliceplanes_height,self.sliceplanes_height[1:]):
                    if height_from <= each_svl.z_high <= height_to:
                        each_svl.last_z_height = height_from
                    else:
                        pass
        self.apply_function_on_group(get_last_layer_each_group)

    def reorder(self):
        def reorder_each_group(each_group):
            reorder_svl_data = []
            sorted_each_group = sorted(each_group, key = lambda d:d.x)

            svl_data_each_groups = []
            for index, groupby_iterator in groupby(sorted_each_group, key = lambda d:d.x):
                svl_data_each_groups.append(list(groupby_iterator))      # Store group iterator as a list

            flip_flop = 0
            for each_data in svl_data_each_groups:
                flip_flop += 1
                if flip_flop % 2:
                    reorder_svl_data += each_data
                else:
                    reorder_svl_data += each_data[::-1]
            return reorder_svl_data

        self.svl_data_group = self.apply_function_on_group(reorder_each_group)

    def index_list_intersect_with_plane(self, plane_height):

        def vertical_line_intersect_horizontal_plane(line_start, line_end, plane_height):
            if line_start < plane_height < line_end:
                return True
            else:
                return False
        
        def return_intersected_svl_data_each_group(each_group):  # change name
            intersected_svl_data = []
            for svl_data in each_group:
                if vertical_line_intersect_horizontal_plane(svl_data.z_low,
                                                            svl_data.z_high,
                                                            plane_height):
                    intersected_svl_data.append(svl_data)
            return intersected_svl_data

        return self.apply_function_on_group(return_intersected_svl_data_each_group)

    def return_polylines(self, sampled_point, plane_height):

        pl = SupportLineStack()
        for each_group in sampled_point:
            pl.new_line()
            for svl_data in each_group:
                this_point_ucscaled = svl_data.return_x_y_2d_point()
                this_point_scaled = scale_point_to_clipper(this_point_ucscaled)

                if svl_data.last_z_height == plane_height:
                    # this point is last point
                    if pl.last_line_is_empty():
                        pass
                    else:
                        pl.new_line()
                    pl.add_point_in_last_line(Last_pointLast_point(this_point_scaled))
                    pl.new_line()
                    continue

                if not this_point_ucscaled == each_group[0]: # if not last point and not first point                    
                    if not pl.last_line_is_empty():
                        last_pointlast_point_unscaled = scale_point_from_clipper(pl.point_at_last_line())

                        if calulate_distance(last_pointlast_point_unscaled, this_point_ucscaled) <= config.LINK_THRESHOLD: # new link line
                            pl.add_point_in_last_line(this_point_scaled)
                        else:
                            pl.new_line()
                            pl.add_point_in_last_line(this_point_scaled)
                    else:
                        pl.add_point_in_last_line(this_point_scaled)

                elif this_point_ucscaled == each_group[0]: # first point
                    pl.add_point_in_last_line(this_point_scaled)

        return pl
        # pl.visualize_all()

    def return_polyline_by_height(self, plane_height, first_layer=False):
        sampled_point = self.index_list_intersect_with_plane(plane_height)
        ls = self.return_polylines(sampled_point, plane_height)

        pyclipper_formatting = PolygonStack([])

        # offset points
        # pyclipper_formatting.add_polygon_stack(ls.offset_point(config.LINE_WIDTH))
         # remove the contacting layer, i.e. one empty layer between support and object
        pyclipper_formatting.add_polygon_stack(ls.offset_last_pointlast_point())

        if first_layer:
            pyclipper_formatting.add_polygon_stack(ls.offset_line(config.LINE_WIDTH))
            # pyclipper_formatting.add_polygon_stack(ls.offset_all(config.LINE_WIDTH))
            # pyclipper_formatting.add_polygon_stack(ls.offset_all(config.LINE_WIDTH*2))
            # pyclipper_formatting.add_polygon_stack(ls.offset_all(config.LINE_WIDTH*3))
        #     pyclipper_formatting.add_polygon_stack(ls.offset_all(config.LINE_WIDTH*4))
        # else:
        #     pyclipper_formatting.add_polygon_stack(ls.offset_point(config.LINE_WIDTH))
            # pyclipper_formatting.add_polygon_stack(ls.offset_point(config.LINE_WIDTH*2))
        
        ls.clean()
        return [ls, pyclipper_formatting]

    def refine(self, sliceplanes_height):
        self.reorder()
        self.add_sliceplanes_height(sliceplanes_height)
        self.get_last_layer()
        # self.clean()

    class Support_Vertical_Line_Data(object):
        def __init__(self, x, y, z_high):
            self.x = x
            self.y = y
            self.z_high = z_high

        def return_support_required_point(self):
            return [self.x, self.y, self.z_high]

        def return_x_y_2d_point(self):
            return [self.x, self.y]

        def __str__(self):

            try:
                return "x:{} y:{} z_high:{} z_low:{} last_z_height:{}".format(self.x, self.y, self.z_high, self.z_low, self.last_z_height)
            except AttributeError:
                try:
                    return "x:{} y:{} z_high:{} z_low:{}".format(self.x, self.y, self.z_high, self.z_low)
                except AttributeError:
                    return "x:{} y:{} z_high:{}".format(self.x, self.y, self.z_high)
                    
class Support:
    def __init__(self, mesh, bbox):
        self.mesh = mesh
        self.mesh.bbox = bbox
        self.mesh.min_x = mesh.min_x() # numpy array
        self.mesh.max_x = mesh.max_x() # numpy array
        self.mesh.min_y = mesh.min_y() # numpy array
        self.mesh.max_y = mesh.max_y() # numpy array
        self.mesh.min_z = mesh.min_z() # numpy array
        self.mesh.max_z = mesh.max_z() # numpy array
        self.mesh.bed_z = self.mesh.bbox.zmin
        self.support_required_mask = self.detect_support_requiring_facet()
        self.groups = self.group_support_area()

        self.support_vertical_line_object = Support_Vertical_lines()

    def detect_support_requiring_facet(self, support_starts_height = 0.1):
        # threshold is cos(theta) value
        # if building_direction is vector [[0], [0], [1]]
        # if threshold is cos(-135 degree) = sqrt(2)/2 = -0.70710678118, means if angle is between 135 and 225 degree then these facet requres support
        cos_overhang_angle = -1 * np.cos(config.SUPPORT_OVERHANG_ANGLE)
        normal_cos_theta = self.mesh.dot_building_direction()
        exceed_threshold_mask = (normal_cos_theta<cos_overhang_angle) # boolean list indicating which triangle requires support 

        # also ignore the facet too close to the bed
        not_too_close_to_bed_mask = (self.mesh.max_z > self.mesh.bed_z + support_starts_height)
        support_required_mask = np.logical_and(exceed_threshold_mask, not_too_close_to_bed_mask)

        return support_required_mask # returns a boolen list indicated which triangles require support

    def group_support_area(self, large_triangle_area_threshold = 5):
        # closeThreshold is average_length_of_triangle
        avg_x = sum(self.mesh.max_x - self.mesh.min_x)/len(self.mesh.min_x)
        avg_y = sum(self.mesh.max_y - self.mesh.min_y)/len(self.mesh.min_y)
        avg_z = sum(self.mesh.max_z - self.mesh.min_z)/len(self.mesh.min_z)
        closeThreshold = np.sqrt(avg_x**2 + avg_y**2 + avg_z**2)

        def connect_connected_component(graph):
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
            support_indexs = set(graph)
            while support_indexs:
                start = support_indexs.pop()
                visited = dfs(graph, start)
                group = list(visited)
                groups.append(group)
                support_indexs = support_indexs - visited
            return groups

        from numpy.linalg import norm

        ## use global index 
        support_triangles_index  = np.where(self.support_required_mask)[0]
        centers = get_center(self.mesh.triangles[support_triangles_index])

        large_triangles_mask = self.mesh.areas.flatten()>large_triangle_area_threshold
        large_triangles_mask = large_triangles_mask[self.support_required_mask]

        triangle_index_and_its_neighbour = {}

        for tri_index in support_triangles_index:
            if tri_index in triangle_index_and_its_neighbour:
                neighbour = triangle_index_and_its_neighbour[tri_index] 
            else:
                neighbour = set()
                triangle_index_and_its_neighbour[tri_index] = neighbour

            triangle = self.mesh.triangles[tri_index]

            this_trangle_center = np.array([triangle[0]+triangle[1]+triangle[2]])/3

            # check with large triangles and the close (in terms of center distance) triangle to this triangle and 
            # see whether it is neighbour, check large triangles is because some triangle might not be close to this triangle
            # because one triangle is large so the centers will be far away
            close_triangles_mask = norm(centers - this_trangle_center, axis=1)<closeThreshold
            test_triangle_mask = np.logical_or(close_triangles_mask, large_triangles_mask)

            test_index = support_triangles_index[test_triangle_mask]
            x, y, z = triangle.tolist()

            for tri_detect_index in test_index:

                try:
                    if tri_index in triangle_index_and_its_neighbour[tri_detect_index]:
                        neighbour.add(tri_detect_index)
                        continue
                except KeyError:
                    triangle_index_and_its_neighbour[tri_detect_index] = set()
                

                tri = self.mesh.triangles[tri_detect_index]

                x_test, y_test, z_test = tri.tolist()

                # one vertex equal then neighbour
                if x == x_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue # check for next triangle, this triangle is already a neighbour, no need to check further
                elif x == y_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                elif x == z_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                elif y == x_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                elif y == y_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                elif y == z_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                elif z == x_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                elif z == y_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                elif z == z_test:
                    neighbour.add(tri_detect_index)
                    triangle_index_and_its_neighbour[tri_detect_index].add(tri_index)
                    continue
                else:
                    pass
        
        groups = connect_connected_component(triangle_index_and_its_neighbour)
        return groups

    def sampling_support_points(self): 
        '''
        by equal distance sampling point on the bounding box and raytrace these points onto the grouped area, 
        if it hits then take it as a support point
        '''

        offset = config.SUPPORT_HORIZONTAL_OFFSET_FROM_PARTS

        for group in self.groups:
            self.support_vertical_line_object.append_group()

            group_tri = self.mesh.triangles[group]        

            min_x = np.min(self.mesh.min_x[group])
            max_x = np.max(self.mesh.max_x[group])
            min_y = np.min(self.mesh.min_y[group])
            max_y = np.max(self.mesh.max_y[group])
            max_z = np.max(self.mesh.max_z[group])

            # thin part sampling distance, rethink whether this is necessary
            config.SUPPORT_SAMPLING_DISTANCESmall = 0.5
            if max_x - min_x < offset:
                x_sample = list(np.arange(min_x, max_x, config.SUPPORT_SAMPLING_DISTANCESmall))
                x_sample.append(max_x)
            else:
                x_sample = list(np.arange(min_x + offset, max_x - offset, config.SUPPORT_SAMPLING_DISTANCE))
                if len(x_sample) > 0 and max_x - x_sample[-1] > offset:
                    x_sample.append(max_x)
            if max_y - min_y < offset:
                y_sample = list(np.arange(min_y, max_y, config.SUPPORT_SAMPLING_DISTANCESmall))
                y_sample.append(max_y)
            else:
                y_sample = list(np.arange(min_y + offset, max_y - offset, config.SUPPORT_SAMPLING_DISTANCE))
                if len(y_sample) > 0 and max_y - y_sample[-1] > offset:
                    y_sample.append(max_y)

            epsilon = 0.01
            for x in x_sample:
                for y in y_sample:
                    x_mask = np.logical_and(self.mesh.min_x[group] <= x, x <= self.mesh.max_x[group])
                    y_mask = np.logical_and(self.mesh.min_y[group] <= y, y <= self.mesh.max_y[group])
                    all_mask = np.logical_and(x_mask, y_mask)
                    
                    ray_trace_tri = group_tri[all_mask]
                    res = ray_trace_mesh([x, y, max_z + epsilon], ray_trace_tri)
                    if res != None:
                        z = res[0]
                        self.support_vertical_line_object.append_svl_data_to_last_group(Support_Vertical_lines.Support_Vertical_Line_Data(x, y, z))
                    else:
                        pass

    def find_support_points_lower_end(self):

        def find_support_lower_end_each_group(support_3d_points):

            for index in range(len(support_3d_points)):
                svl_data = support_3d_points[index]
                svl_data.z_low = self.mesh.bed_z

                mask_x = np.logical_and(max_x_list>svl_data.x, min_x_list<svl_data.x)
                mask_y = np.logical_and(max_y_list>svl_data.y, min_y_list<svl_data.y)
                mask_z = (min_z_list<svl_data.z_high-epsilon)

                # len(np.where(mask_z&mask_x&mask_y)[0]) == 0 means there is no triangles under the ray
                for tri_index in np.where(mask_z&mask_x&mask_y)[0]: 
                    triangle = self.mesh.triangles[tri_index]
                    does_exist_intersection, intersect_z_value = ray_triangle_intersection(svl_data.return_support_required_point(), triangle)
                    if does_exist_intersection:
                        svl_data.z_low = intersect_z_value
                    else:
                        pass

            # return z_triangle_selfsupport

        epsilon = 0.1
        bed_z = self.mesh.bed_z
        min_z_list = self.mesh.min_z
        min_x_list = self.mesh.min_x
        max_x_list = self.mesh.max_x
        min_y_list = self.mesh.min_y
        max_y_list = self.mesh.max_y

        self.support_vertical_line_object.apply_function_on_group(find_support_lower_end_each_group)
        

    def create_support_vertical_lines(self): # change function name to create support vertical line data
        self.sampling_support_points()
        self.find_support_points_lower_end()

    def refine_support_vertical_lines(self, sliceplanes_height):
        self.support_vertical_line_object.refine(sliceplanes_height)
 
    def get_support_polylines_list(self):

        BBox = self.mesh.bounding_box()
        slice_height_from = BBox.zmin
        slice_height_to = BBox.zmax
        slice_step = config.LAYER_THICHNESS

        slice_height_from += 0.198768976
        slice_height_to += 0.198768976
        sliceplanes_height = np.arange(slice_height_from, slice_height_to, slice_step)

        # make and refine support vertical lines
        self.create_support_vertical_lines()
        self.refine_support_vertical_lines(sliceplanes_height)

        # return polylines from support vertical lines
        polylines_all = []
        layer_counter = 0
        for height in sliceplanes_height:
            if layer_counter <= config.bed_support_strengthen_number - 1:
                polylines_by_height = self.support_vertical_line_object.return_polyline_by_height(height, first_layer = True) 
            else:
                polylines_by_height = self.support_vertical_line_object.return_polyline_by_height(height, first_layer = False) 

            polylines_all.append(polylines_by_height)
            layer_counter += 1

        return polylines_all

    def visulisation(self, require_group = False, require_support_lines = False):


        BBox = self.mesh.bounding_box()
        slice_height_from = BBox.zmin
        slice_height_to = BBox.zmax
        slice_step = config.LAYER_THICHNESS

        slice_height_from += 0.198768976
        slice_height_to += 0.198768976
        sliceplanes_height = np.arange(slice_height_from, slice_height_to, slice_step)

        ############# visulisation ####################
        from mpl_toolkits import mplot3d
        import matplotlib.pyplot as plt

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

                if len(self.groups) > 50:
                    c_n = 'r'
                else:
                    c_n = next(cname)

                for index in group:
                    colors[index] = c_n

        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.mesh.triangles, color=colors))
        # Auto scale to the mesh size
        scale = np.array([self.mesh.triangles[:,0], self.mesh.triangles[:,1], self.mesh.triangles[:,2]]).flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)

        if require_support_lines:
            self.create_support_vertical_lines()
            self.refine_support_vertical_lines(sliceplanes_height)

            for group in self.support_vertical_line_object:
                if len(self.support_vertical_line_object) > 50:
                    c_n = 'r'
                else:
                    c_n = next(cname)
                for svl_data in group:
                    plt.plot([svl_data.x, svl_data.x],
                             [svl_data.y, svl_data.y],
                             [svl_data.z_low,svl_data.z_high], 
                             color = c_n)
        plt.show()

############################## end of support by mesh ########################

############################## support by layer ##############################
def generate_support_from_layer_list(layer_list):
    for layer_index in reversed(range(len(layer_list))):
        one_last_layer_index = layer_index - 1
        if layer_index == 0:
            break
        layer_list[one_last_layer_index].support_required_ps = \
            layer_list[layer_index].process_support()

    if config.ONE_EMPTY_LAYER_BETWEEN_SUPPORT_AND_MODEL:
        for layer_index in range(len(layer_list)):
            one_above_layer_index = layer_index + 1
            if layer_index == len(layer_list) - 1:
                break

            this_layer_support_required_ps = \
                layer_list[layer_index].support_required_ps

            one_above_layer_ps = \
                layer_list[one_above_layer_index].support_required_ps

            last_layer_area = \
                this_layer_support_required_ps.difference_with(one_above_layer_ps)

            this_layer_support_required_ps = \
                this_layer_support_required_ps.difference_with(last_layer_area)

            layer_list[layer_index].support_required_ps = \
                this_layer_support_required_ps
############################## end of support by layer ########################


def main():
    from stl import mesh as np_mesh
    from mp5slicer.mesh_processing import mesh_operations
    import datetime
    # import mp5slicer.config.config as config
    config.reset()
    start_time = datetime.datetime.now()
    mesh_name = "reaper.stl"
    stl_mesh = np_mesh.Mesh.from_file(mesh_name)
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True)
    bbox = our_mesh.bounding_box()
    sup = Support(our_mesh, bbox)
    sup.visulisation(require_group=True, require_support_lines=True)

if __name__ == '__main__':
    main()