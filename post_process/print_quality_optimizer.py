import slicer.config.config as config
import numpy as np
from slicer.commons.utils import distance as calulate_distance

def shorten_last_line(line_group, shorten_length):
    if config.inner_boundary_coast_at_end_length <= 0:
        return None

    import copy 
    def shorten_vector(end, shorten_length_in_function): # start is 0,0
        import numpy as np
        shorten_length_in_function = np.sqrt(shorten_length_in_function)

        angle = np.arctan2(end[1],end[0])
        length_of_end = np.sqrt(end[0]**2 + end[1]**2)

        if length_of_end < shorten_length_in_function:
            return length_of_end# last line is less than 0.8

        if end[0] == 0:
            shorten_length_ratio_x = 0
        else:
            shorten_length_ratio_x = abs((length_of_end - shorten_length_in_function)*np.cos(angle)/end[0])
            
        if end[1] == 0:
            shorten_length_ratio_y = 0
        else:
            shorten_length_ratio_y = abs((length_of_end - shorten_length_in_function)*np.sin(angle)/end[1])
            
        assert 0 <= shorten_length_ratio_x <= 1
        assert 0 <= shorten_length_ratio_y <= 1
        
        answer = [end[0]*shorten_length_ratio_x, end[1]*shorten_length_ratio_y]
        return answer

    index_change = 0
    for index in range(len(line_group.sub_lines)):   
        index += index_change
        shorten_length_copy = copy.copy(shorten_length)
        while shorten_length_copy > 0:
            # print('in while')
            each_line = line_group.sub_lines[index]    
            if len(each_line) > 2:
                # print('in if')
                each_line = line_group.sub_lines[index]
                vector_from_last_line = [each_line[-1][0] - each_line[-2][0], each_line[-1][1] - each_line[-2][1]]
                final_vector = shorten_vector(vector_from_last_line, shorten_length_copy)
                if isinstance(final_vector, float): # last line shorter than shorten_length_copy,then delete last line
                    shorten_length_copy -= final_vector
                    original_end_point = line_group.sub_lines[index][-1]
                    line_group.sub_lines[index] = line_group.sub_lines[index][:-1]
                    line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
                    index_change += 1 # counting the line added to the subline
                else:
                    final_end_point = [final_vector[0] + each_line[-2][0], final_vector[1] + each_line[-2][1]]
                    original_end_point = line_group.sub_lines[index][-1]
                    line_group.sub_lines[index][-1] = final_end_point
                    line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
                    index_change += 1 # counting the line added to the subline
                    break
            else:
                break
            # original_end_point = line_group.sub_lines[index][-1] 
            # line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
    return line_group

def reorder_lines_close_to_point(line_group, point):
    if point == None:
        return None

    for line_index in range(len(line_group.sub_lines)):
        # line_group format has the first point equals to last point, so delete it for easier mulipulation
        line = line_group.sub_lines[line_index][:-1] 

        shortest_length = 9999999999

        for point_index in range(len(line)):
            length = calulate_distance(point, line[point_index])
            if length < shortest_length:
                shortest_length = length
                shortest_length_index = point_index

        new_line = []
        for i in range(shortest_length_index, len(line)):
            new_line.append(line[i])
        for i in range(shortest_length_index):
            new_line.append(line[i])

        new_line.append(new_line[0]) # forcing the format for line_group
        line_group.sub_lines[line_index] = new_line

def retract_at_point_inside_boundary(line_group, inner_boundary_first_point_list):
    if config.outline_outside_in:
        return None
    if not config.boundary_retraction_inside:
        return None
    if inner_boundary_first_point_list == None:
        return None
    if config.shellSize == 0:
        return None
    if inner_boundary_first_point_list == []:
        return None

    epsilon = 0.01
    index_change = 0
    for outer_boundary_index in range(len(line_group.sub_lines)):
        outer_boundary_index += index_change
        outer_boundary_first_point = line_group.sub_lines[outer_boundary_index][0]
        
        for point in inner_boundary_first_point_list:
            distance = calulate_distance(point, line_group.sub_lines[0][0]) 
            if config.line_width*(config.shellSize) - epsilon <= distance <= config.line_width*config.shellSize + epsilon:
                retraction_point = point # this is the optimal retraction point so exit the loop
                break
            elif config.line_width*(config.shellSize-1) <= distance <= config.line_width*(config.shellSize) + epsilon:
                retraction_point = point
            else:
                pass

        try:
            retraction_point
        except UnboundLocalError:
            return None

        # line_group.sub_lines[outer_boundary_index].append(retraction_point) 
        if retraction_point != None:
            line_group.sub_lines.insert(outer_boundary_index+1,[retraction_point]) # tricking the gcode write to go to a new point
            index_change += 1

