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
            return length_of_end# last line is less than 0.8

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
        while shorten_length > 0:
            each_line = line_group.sub_lines[index]    
            if len(each_line) > 2:
                each_line = line_group.sub_lines[index]
                vector_from_last_line = [each_line[-1][0] - each_line[-2][0], each_line[-1][1] - each_line[-2][1]]
                final_vector = shorten_vector(vector_from_last_line, shorten_length)
                if isinstance(final_vector, float): # last line shorter than shorten_length,then delete last line
                    shorten_length -= final_vector
                    original_end_point = line_group.sub_lines[index][-1]
                    line_group.sub_lines[index] = line_group.sub_lines[index][:-1]
                    line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
                else:
                    final_end_point = [final_vector[0] + each_line[-2][0], final_vector[1] + each_line[-2][1]]
                    original_end_point = line_group.sub_lines[index][-1]
                    line_group.sub_lines[index][-1] = final_end_point
                    line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
                    break
            else:
                break
        else:
            pass
            # original_end_point = line_group.sub_lines[index][-1] 
            # line_group.sub_lines.insert(index+1,[original_end_point]) # tricking the gcode write to go to a new point
        return line_group

def reorder_lines_close_to_point(point, line_group):

    for line_index in range(len(line_group.sub_lines)):
        # line_group format has the first point equals to last point, so delete it for easier mulipulation
        line = line_group.sub_lines[line_index][:-1] 

        shortest_length = 9999999999

        for point_index in range(len(line)):
            length = dist(point, line[point_index])
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