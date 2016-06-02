import numpy as np

cimport numpy as np






def intersection_with_line(float z, float *vertice_0, float *vertice_1):
    cdef:
      float low[3]
      float high[3]
      float r
      float S[3]
    if vertice_0[2]< vertice_1[2]:
        low = vertice_1
        high = vertice_0
    else:
        low = vertice_0
        high = vertice_1
    if z < high[2] or z> low[2]:
        if high[2] == z:
            return high
        elif low[2] == z:
            return low
        else:
            return None
    else :
        r = (z - low[2]) / (high[2] - low[2])

        S[0] = low[0] + (r * (high[0]- low[0]))
        S[1] = low[1] + (r * (high[1] - low[1]))
        S[2] = 0
        return S
