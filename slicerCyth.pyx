import numpy as np





def intersection_with_line(z, vertice_0, vertice_1):
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

        S = np.array([low[0] + (r * (high[0]- low[0])),
                      low[1] + (r * (high[1] - low[1])),
                     0])
        return S
