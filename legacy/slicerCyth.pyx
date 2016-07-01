from __future__ import division
import numpy as np
cimport numpy as np






cdef int intersection_with_line(double[::1] S , float z, double[::1]  vertice_0, double[::1]  vertice_1) :
    cdef:
      double[::1]  low
      double[::1] high
      double r
    if vertice_0[2]< vertice_1[2]:
        low = vertice_1
        high = vertice_0
    else:
        low = vertice_0
        high = vertice_1
    if z < high[2] or z> low[2]:
        if high[2] == z:
            S = high
            return 1
        elif low[2] == z:
            S = low
            return 1
        else:
            return 0
    else :
        r = (z - low[2]) / (high[2] - low[2])

        S[0] = low[0] + (r * (high[0]- low[0]))
        S[1] = low[1] + (r * (high[1] - low[1]))
        S[2] = 0
        return 1


cdef int intersection_with_triangle(double[:,::1] line , z,double[:,::1] triangle) :

    cdef:
      double S[3]
      double[::1] vertice_0
      double[::1] vertice_1
      double[::1] vertice_2
      int index = 0

    vertice_0 = triangle[0]
    vertice_1 = triangle[1]
    vertice_2 = triangle[2]




    if vertice_0[2] == z:
        if vertice_1[2] == z:
            if  vertice_2[2] != z:
                line[0]= vertice_0
                line[1] = vertice_1
                return 1
            else:
                return 0
        if vertice_2[2] == z:
            if  vertice_1[2] != z:
                line[0]= vertice_0
                line[1] = vertice_2
                return 1
            else:
                return 0
    if vertice_1[2] == z:
        if vertice_2[2] == z:
            if  vertice_0[2] != z:
                line[0]= vertice_0
                line[1] = vertice_1
                return 1
            else:
                return 0

    if intersection_with_line(S ,z,vertice_0, vertice_1) :
        line[index] = S
        index = index +  1

    if intersection_with_line(S, z,vertice_1, vertice_2) :
        line[index] = S
        index = index +  1

    if intersection_with_line(S, z,vertice_0, vertice_2) :
        line[index] = S

    if len(line) != 2:
        raise RuntimeError


    return 1




def min_max_z(triangle):
    return [np.min(triangle[:,2]), np.max(triangle[:,2])]




def slicer_from_mesh_as_dict_cyth(mesh, float slice_height_from, float slice_height_to,float slice_step):
    cdef :
      double [:,::1] tri
      double line[2][3]
      # float [::1] sliceplanes_height

    # height = slice_height_from + 0.198768976
    slice_height_from += 0.198768976
    slice_height_to += 0.198768976


    # while height < slice_height_to:
    #   sliceplanes_height.append(heigth)
    #   heigth = height + slice_step
    sliceplanes_height = np.arange(slice_height_from, slice_height_to, slice_step)
    slice_layers = [{} for i in range(len(sliceplanes_height))]

    for triangle in mesh.triangles:

        tri = triangle
        tri_min, tri_max = min_max_z(triangle)
        intersect_planes_heights = sliceplanes_height[(tri_min<=sliceplanes_height)&(sliceplanes_height<=tri_max)]
        plane_index = np.where((tri_min<=sliceplanes_height)&(sliceplanes_height<=tri_max))[0]

        planes = [height for height in intersect_planes_heights]
        for index, height in zip(plane_index, planes):

            if intersection_with_triangle(line, height, tri):
            # if isinstance(line, list):
                # line[0] =line[0][:2]
                # line[1] =line[1][:2]
                #
                #
                # line[0] = line[0].tolist()
                # line[1] = line[1].tolist()
                # for point_index in range(len(line)):
                #     for val_index in range(len(line[point_index])):
                #         line[point_index][val_index] = truncate(line[point_index][val_index],8)

                point1 = tuple(line[0])

                point2= tuple(line[1])
                try:
                    if point2 not in slice_layers[index][point1]:
                        slice_layers[index][point1].append(point2)
                except:
                    slice_layers[index][point1] = []
                    slice_layers[index][point1].append(point2)
                try:
                    if point1 not in slice_layers[index][point2]:
                        slice_layers[index][point2].append(point1)
                except:
                    slice_layers[index][point2] = []
                    slice_layers[index][point2].append(point1)

    return slice_layers
