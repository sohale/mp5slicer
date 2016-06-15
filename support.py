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

def return_lr_offset_polyline(line,offset_value,does_visualize=False, end_point=None):
    '''
    This is an algorithm to offset lines with degrees between two consecutive line with degree 45*n, n integer.
    '''
    import numpy as np
    assert end_point in [None, 'l', 'r']
    line = np.array(line)
    line_y_scale = np.linalg.norm(line[1] - line[0])
    length = line_y_scale
    length_half = length/2
    
    angle = np.arctan2(line[1][1] - line[0][1], line[1][0] - line[0][0])

    line_start_x = line[0][0]
    line_start_y = line[0][1]

    line_end_x = line[1][0]
    line_end_y = line[1][1]

    center = [(line_end_x-line_start_x )/2, ( line_end_y-line_start_y)/2]
    
    line_off_set = [
                    [-length_half-offset_value/2, -offset_value/2],
                    [-length_half-offset_value/2, offset_value/2],
                    [length_half+ offset_value/2, offset_value/2],
                    [length_half+ offset_value/2, -offset_value/2]]
    
    line_off_set = np.array(line_off_set)

    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],[np.sin(angle), np.cos(angle)]])
    res = []
    for i in line_off_set:
        res.append(list(np.dot(rotation_matrix,i)))  
        
    res = [[i[0]+center[0],i[1]+center[1] ] for i in res]
    res = [[i[0]+line_start_x,i[1]+line_start_y ] for i in res]

    polygon = [res[0],res[1],res[2],res[3]]

    if does_visualize:
        import matplotlib.pyplot as plt
        point_off_set = polygon
        plt.plot([line[0][0],line[1][0]],[line[0][1],line[1][1]],'b--')
        for i in range(len(point_off_set)-1):
            plt.plot([point_off_set[i][0],point_off_set[i+1][0]],[point_off_set[i][1], point_off_set[i+1][1]])
        plt.plot([point_off_set[len(point_off_set)-1][0],point_off_set[0][0]],[point_off_set[len(point_off_set)-1][1], point_off_set[0][1]])
        plt.show()
        for i in range(len(res)):
            plt.plot(res[i][0],res[i][1],'ro')


    res = np.array(res)
    
    if end_point == 'l': # return the left offset line 
        return (res[0], res[1])
    elif end_point == 'r': # return the right offset line 
        return (res[2], res[3])
    elif end_point == None: # return the up and down offset line 
        return ([res[1],res[2]], [res[3],res[0]])

def seg_intersect(lines):

    line1, line2 = lines

    if np.allclose([line1[0][0], line1[1][0], line2[0][0], line2[1][0]],line1[0][0],atol=0.01): # horizontal
        return line2[0]
    if np.allclose([line1[1][1], line1[1][1], line2[0][1], line2[1][1]],line1[0][1],atol=0.01): # vertical
        return line2[0]

    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return 'line', line1[1], line2[0]
        # raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return [x, y]

def seg_intersect_bounding_box(lines):

    line1, line2 = lines
    if np.allclose([line1[0][0], line1[1][0], line2[0][0], line2[1][0]],line1[0][0],atol=0.01): # horizontal
        return False
    if np.allclose([line1[1][1], line1[1][1], line2[0][1], line2[1][1]],line1[0][1],atol=0.01): # vertical
        return False

    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return False
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    xmin = np.min([line1[0][0],line1[1][0]])
    xmax = np.max([line1[0][0],line1[1][0]])
    ymin = np.min([line1[0][1],line1[1][1]])
    ymax = np.max([line1[0][1],line1[1][1]])
    if (xmin+0.1<=x<=xmax-0.1) and (ymin+0.1<=y<=ymax-0.1):
        return True
    else:
        return False

def polylines_from_offset_polygon(lines, offset_value):
    result = []
    for i in lines:
        result.append(return_lr_offset_polyline(i, offset_value))

    l_all = [i[0] for i in result]
    left_end = return_lr_offset_polyline(lines[0],offset_value,end_point='l')
    right_end = return_lr_offset_polyline(lines[-1],offset_value,end_point='r')
    r_all = [i[1] for i in result]
    
    # import numpy as np
    # import pylab as pl
    # from matplotlib import collections  as mc
    # import matplotlib.pyplot as plt

    # lc = mc.LineCollection(l_all, linewidths=2)
    # fig, ax = pl.subplots()
    # ax.add_collection(lc)
    # ax.autoscale()
    # ax.margins(0.1)
    # plt.show()

    res =  [] 
    res.append(left_end)
    for i in l_all:
        res.append(i)
    res.append(right_end)
    for i in r_all[::-1]:
        res.append(i)
    intersections = []
    
    for index in range(len(res)-1):
        if index == len(res):
            intersect = seg_intersect([res[index], res[0]])
        else:
            intersect = seg_intersect([res[index], res[index+1]])

        if intersect == 'two_perpendicular_lines':
            # print('=======================')
            # print([res[index], res[index-1]])
            # print(l_all[-1])
            # print(l_all[-2])
            # print(len(res))

            raise Tiger

        if intersect[0] == 'line':
            intersections.append(intersect[1])
            intersections.append(intersect[2])
        else:
            intersections.append(intersect)

    polylines = [[intersections[index], intersections[index+1]] for index in range(len(intersections)-1)]
    polylines.append([intersections[-1],left_end[0]])
    polylines.append([left_end[0],left_end[1]])

    # import numpy as np
    # import pylab as pl
    # from matplotlib import collections  as mc

    # lc = mc.LineCollection(polylines, linewidths=2)
    # fig, ax = pl.subplots()
    # ax.add_collection(lc)
    # ax.autoscale()
    # ax.margins(0.1)
    # pl.show()

    return polylines

def get_center(mesh_triangles):
    return (mesh_triangles[:,0] + mesh_triangles[:,1] + mesh_triangles[:,2])/3

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
        self.groups = self.group_support_area(save_cache=True, use_cache=True)
        

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
        # not_too_close_to_bed_mask = (self.mesh.max_z > self.mesh.bed_z + support_starts_height)
        # support_required_mask = np.logical_and(exceed_threshold_mask, not_too_close_to_bed_mask)

        return exceed_threshold_mask # returns a boolen list indicated which triangles require support

    def group_support_area(self, save_cache = False, use_cache=False):

        if use_cache:
            import os.path
            if os.path.isfile(self.mesh.name + '.txt'):
                import json
                with open(self.mesh.name+'.txt') as data_file:   
                     data = json.load(data_file)
                if data['supportOverhangangle'] == config.supportOverhangangle:
                    print('using cache groups')
                    return data['groups']
                else:
                    print('computing groups because of different supportOverhangangle to Cache')

        import datetime
        start_time = datetime.datetime.now()

        support_triangles_index  = np.where(self.support_required_mask)[0]

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
        
        if save_cache:
            groups = [[int(j) for j in i] for i in groups]
            data = {}
            data['supportOverhangangle'] = config.supportOverhangangle
            data['groups'] = groups
            import json
            with open(self.mesh.name+'.txt', 'w') as outfile:
                json.dump(data, outfile)

        return groups

    def sampling_support_points(self, offset_boundingbox = config.layerThickness): 
        '''
        by equal distance sampling point on the bounding box and raytrace these points onto the grouped area, 
        if it hits then take it as a support point
        '''
        support_points_by_group = []

        for group in self.groups:
            support_points = []
            support_points_by_group.append(support_points)

            group_tri = self.mesh.triangles[group]
################################################# revisit this #################################################################
            # min_x = np.min(self.mesh.min_x[group] + config.layerThickness*3)
            # max_x = np.max(self.mesh.max_x[group] - config.layerThickness*3)
            # min_y = np.min(self.mesh.min_y[group] + config.layerThickness*3)
            # max_y = np.max(self.mesh.max_y[group] - config.layerThickness*3)
            # min_z = np.min(self.mesh.min_z[group] + config.layerThickness*3)
            # max_z = np.max(self.mesh.max_z[group] - config.layerThickness*3)            


            min_x = np.min(self.mesh.min_x[group] + offset_boundingbox)
            max_x = np.max(self.mesh.max_x[group] - offset_boundingbox)
            min_y = np.min(self.mesh.min_y[group] + offset_boundingbox)
            max_y = np.max(self.mesh.max_y[group] - offset_boundingbox)
            min_z = np.min(self.mesh.min_z[group] + offset_boundingbox)
            max_z = np.max(self.mesh.max_z[group] - offset_boundingbox)

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

    def arranged_polyline_from_support(self, support_line_starts_list_by_group, support_line_ends_list_by_group, height, does_visualize = False, first_layer=False):

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

        def distance_between_two_point(point_start, point_end):
            import numpy as np
            point_start = np.array(point_start)
            point_end = np.array(point_end)
            return np.linalg.norm(point_start - point_end)

        polylines_connected = []
        for traverse_points in traverse_points_by_groups:
            polylines_connected.append([])
            for i in range(len(traverse_points) - 1):
                point_start = traverse_points[i]
                point_end = traverse_points[i+1]
                # polylines += [[point_start, point_end]]
                import numpy as np
                if distance_between_two_point(point_start, point_end) <=  np.sqrt(2*(config.supportSamplingDistance**2)):
                    polylines_connected[-1].append([point_start, point_end]) # coneected polylines
                    
                else:
                    # import numpy as np
                    # import pylab as pl
                    # from matplotlib import collections  as mc
                    # import matplotlib.pyplot as plt

                    # lc = mc.LineCollection(polylines_connected[-1], linewidths=2)
                    # fig, ax = pl.subplots()
                    # ax.add_collection(lc)
                    # ax.autoscale()
                    # ax.margins(0.1)
                    # plt.show()

                    polylines_connected.append([])

        def reorder(polylines_connected): # sorted by starting point, first by x then y
            import numpy as np
            polylines_connected = np.array(polylines_connected)
            order_recorder = [] # index, starting point
            counter = 0
            for i in polylines_connected:
                if i: # if not empty 
                    order_recorder.append([counter, i[0][0]])
                counter += 1
            import itertools 


            res = []
            for _,grouped_result in itertools.groupby(order_recorder,  key=lambda item: item[1][0]):
                res.append([_,list(grouped_result)])
            res = sorted(res, key=lambda item:item[0])
    
            flip_counter = True

            new_order = []
            for _, group in res:
                group_index = [i[0] for i in group]
                if flip_counter:
                    new_order += group_index[::-1]
                    flip_counter = False
                else:
                    new_order += group_index
                    flip_counter = True

            print(new_order)
            return polylines_connected[new_order]

        polylines_connected = reorder(polylines_connected)

        polylines = []
        for each_connected_polylines in polylines_connected:
            if len(each_connected_polylines) != 0:
                polylines += each_connected_polylines
                polyline = polylines_from_offset_polygon(each_connected_polylines, 0.4)
                polylines += polyline
                if first_layer:
                    polyline = polylines_from_offset_polygon(each_connected_polylines, 0.8)
                    polylines += polyline
                    # polyline = polylines_from_offset_polygon(each_connected_polylines, 1.2)
                    # polylines += polyline

                # print([return_offset_polygon(p) for p in each_polylines])

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
    mesh_name = "bunny_half_foot_only.stl"
    stl_mesh = np_mesh.Mesh.from_file(mesh_name)
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True, name=mesh_name)
    our_mesh.name = mesh_name
    sup = Support(our_mesh)
    # a = sup.get_support_polylines_list()
    # polylines = sup.get_support_polylines_list()
    sup.visulisation(require_group = True, require_support_lines = True)


def main():
    from stl import mesh as np_mesh
    import mesh_operations
    import numpy as np

    import datetime
    start_time = datetime.datetime.now()
    mesh_name = "bunny_half.stl"
    stl_mesh = np_mesh.Mesh.from_file(mesh_name)
    our_mesh = mesh_operations.mesh(stl_mesh.vectors, fix_mesh=True, name=mesh_name)
    our_mesh.name = mesh_name
    sup = Support(our_mesh)
    s,e = sup.support_lines()
    sup.arranged_polyline_from_support(s,e,0.5,does_visualize=False)
    # sup.visulisation(require_support_lines=True)

if __name__ == '__main__':
    main()