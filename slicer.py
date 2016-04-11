import numpy as np
from collections import namedtuple
from mpmath import fp
import decimal

class Plane:
    def __init__(self, normal, z):
        self.normal = normal
        self.z = z

    def distance_to_vertice(self, vertice):
        assert isinstance(vertice, np.ndarray)
        dot = np.dot(vertice, self.normal)
        distance = dot - self.z
        assert len(distance) == 1
        return distance[0]

    def intersection_with_line_segment(self, vertice_0, vertice_1):
        dist_0 = self.distance_to_vertice(vertice_0)
        dist_1 = self.distance_to_vertice(vertice_1)
    
        if dist_0*dist_1 > 0:
            return None
        else:
            t =  dist_0 /  float(dist_0 - dist_1)
            outP = vertice_0 + t * (vertice_1 - vertice_0)

            return outP



    def intersection_with_triangle(self, triangle):
        # triangle is a 3*3 matrix
        assert isinstance(triangle, np.ndarray)
        if(np.array_equal(triangle[0],triangle[1])):
            return []
        if(np.array_equal(triangle[0],triangle[2])):
            return []
        if(np.array_equal(triangle[2],triangle[1])):
            return []
        vertice_0 = triangle[0]
        vertice_1 = triangle[1]
        vertice_2 = triangle[2]
        
        line = []
        intersection_point_0 = self.intersection_with_line_segment(vertice_0, vertice_1)
        if intersection_point_0 is not None:
            line.append(intersection_point_0)

        intersection_point_1 = self.intersection_with_line_segment(vertice_1, vertice_2)
        if intersection_point_1 is not None:
            line.append(intersection_point_1)

        intersection_point_2 = self.intersection_with_line_segment(vertice_0, vertice_2)
        if intersection_point_2 is not None:
            line.append(intersection_point_2)
        
        return line

def min_max_z(triangle):
    return [np.min(triangle[:,2]), np.max(triangle[:,2])]

def slicer(stl_filepath, slice_height_from=0, slice_height_to=100, slice_step=1):
    from stl import mesh

    your_mesh = mesh.Mesh.from_file(stl_filepath)

    return slicer_from_mesh(your_mesh, 
                            slice_height_from=slice_height_from, 
                            slice_height_to=slice_height_to, 
                            slice_step=slice_step)

def slicer_from_mesh(mesh, slice_height_from=0, slice_height_to=100, slice_step=1):

    normal = np.array([[0.],[0.],[1.]], dtype=np.dtype(decimal.Decimal))

    sliceplanes_height = np.arange(slice_height_from, slice_height_to, slice_step)
    slice_layers = [[] for i in range(len(sliceplanes_height))]

    for triangle in mesh.triangles:
        tri_min, tri_max = min_max_z(triangle)
        intersect_planes_heights = sliceplanes_height[(tri_min<sliceplanes_height)&(sliceplanes_height<tri_max)]
        plane_index = np.where((tri_min<sliceplanes_height)&(sliceplanes_height<tri_max))[0]

        planes = [Plane(normal=normal, z=height) for height in intersect_planes_heights]
        for index, plane in zip(plane_index, planes):
            line = plane.intersection_with_triangle(triangle)
            slice_layers[index].append([list(i) for i in line])

    return slice_layers

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return float('.'.join([i, (d+'0'*n)[:n]]))

def slicer_from_mesh_as_dict(mesh, slice_height_from=0, slice_height_to=100, slice_step=1):
    import decimal

    normal = np.array([[0.],[0.],[1.]])
    # ufunc = np.vectorize(lambda x: truncate(x,8))


    sliceplanes_height = np.arange(slice_height_from, slice_height_to, slice_step)
    slice_layers = [{} for i in range(len(sliceplanes_height))]

    for triangle in mesh.triangles:
        tri_min, tri_max = min_max_z(triangle)
        intersect_planes_heights = sliceplanes_height[(tri_min<sliceplanes_height)&(sliceplanes_height<tri_max)]
        plane_index = np.where((tri_min<sliceplanes_height)&(sliceplanes_height<tri_max))[0]

        planes = [Plane(normal=normal, z=height) for height in intersect_planes_heights]
        for index, plane in zip(plane_index, planes):
            line = plane.intersection_with_triangle(triangle)
            line[0] =line[0][:2]
            # print(type(line[0][0]))
            # ufunc(line[0])
            line[1] =line[1][:2]
            # ufunc(line[1])


            line[0] = line[0].tolist()
            line[1] = line[1].tolist()
            for point_index in range(len(line)):
            # #     # for val_index in range(len(line[point_index])):
            # #     #     line[point_index][val_index] = round(line[point_index][val_index],2)
            # #     # line[point_index] = line[point_index].tolist()
                for val_index in range(len(line[point_index])):
                    line[point_index][val_index] = truncate(line[point_index][val_index],8)

            point1 = tuple(line[0])

            point2= tuple(line[1])
            try:
                slice_layers[index][point1].append(point2)
            except:
                slice_layers[index][point1] = []
                slice_layers[index][point1].append(point2)
            try:
                slice_layers[index][point2].append(point1)
            except:
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

if __name__ == '__main__':
    import datetime
    start = datetime.datetime.now()
    slice_layers = slicer('FLATFOOT_StanfordBunny_jmil_HIGH_RES_Smoothed.stl', slice_height_from=0, slice_height_to=100, slice_step=1)
    print(datetime.datetime.now() - start)
    visualization_2d(slice_layers)
