import slicer.config.config as config


def dist(point1, point2):
     return pow((point1[0]-point2[0]),2) + pow((point1[1]-point2[1]),2)

def shorten_last_line(line_group, shorten_length):
    def shorten_vector(end, shorten_length): # start is 0,0
        import numpy as np
        shorten_length = np.sqrt(shorten_length)
        angle = np.arctan2(end[1],end[0])
        length_of_end = np.sqrt(end[0]**2 + end[1]**2)

        if length_of_end < shorten_length:
            return None # last line is less than 0.8

        if end[0] == 0:
            shorten_length_ratio_x = 0
        else:
            shorten_length_ratio_x = abs((length_of_end - shorten_length)*np.cos(angle)/end[0])
            
        if end[1] == 0:
            shorten_length_ratio_y = 0
        else:
            shorten_length_ratio_y = abs((length_of_end - shorten_length)*np.sin(angle)/end[1])
            
        assert 0 <= shorten_length_ratio_x <= 1
        assert 0 <= shorten_length_ratio_y <= 1
        
        answer = [end[0]*shorten_length_ratio_x, end[1]*shorten_length_ratio_y]
        return answer

    for index in range(len(line_group.sub_lines)):       

        each_line = line_group.sub_lines[index]
        if len(each_line) > 2:
            vector_from_last_line = [each_line[-1][0] - each_line[-2][0], each_line[-1][1] - each_line[-2][1]]
            final_vector = shorten_vector(vector_from_last_line, shorten_length)
            if final_vector == None: # last line shorter than shorten_length,then delete last line
                original_end_point = line_group.sub_lines[index][-1]
                line_group.sub_lines[index] = line_group.sub_lines[index][:-1]
                line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
            else:
                final_end_point = [final_vector[0] + each_line[-2][0], final_vector[1] + each_line[-2][1]]
                original_end_point = line_group.sub_lines[index][-1]
                line_group.sub_lines[index][-1] = final_end_point
                line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point

        else:
            pass
            # original_end_point = line_group.sub_lines[index][-1] 
            # line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
import math
def calculE(A, B):


    def truncate(f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        s = '{}'.format(f)
        if 'e' in s or 'E' in s:
            return float('{0:.{1}f}'.format(f, n))
        i, p, d = s.partition('.')
        return float('.'.join((i, (d+'0'*n)[:n])))

    # Calculate the extrusion for a straight movement from A to B
    distance = math.sqrt( (pow((A[0]-B[0]),2)) + pow((A[1]-B[1]),2))
    section_surface = config.layerThickness * config.line_width # layerThickness is possible to change for each layer
    assert config.layerThickness != None
    assert config.line_width != None
    volume = section_surface * distance * config.extrusion_multiplier
    filament_length = volume / config.crossArea
    filament_length = truncate(filament_length, 4)
    return filament_length