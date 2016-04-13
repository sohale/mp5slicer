import bintrees


def arrange_path(lines):


    start_points_list = [None]*len(lines)
    end_points_list = [None]*len(lines)
    for line_index in range(len(lines)):
        start_points_list[line_index] = lines[line_index][0]
        end_points_list[line_index] = lines[line_index][len(lines[line_index])-1]

    end_offset = len(lines)

    already_used_points = [False]*(len(lines)*2)

    ordered_lines = []
    current_index = 0
    end_point = True #the end point in the new referential is also an end point in the unordered referential


    while(len(ordered_lines)< len(lines)):


        if end_point:#search with begining point
            # reversed_list = lines[current_index]
            lines[current_index].reverse()
            ordered_lines.append(lines[current_index])


        else: #search with end point
            ordered_lines.append(lines[current_index])

        if (len(ordered_lines)< len(lines)):
            already_used_points[current_index] = True
            already_used_points[current_index + end_offset] = True
            next_point_tuple = get_next_point(current_index,end_point, start_points_list, end_points_list, already_used_points, end_offset)
            current_index = next_point_tuple[1] % (len(lines))
            end_point = next_point_tuple[2]

    return ordered_lines

def get_next_point(init_point_index, end_point, start_points_list, end_points_list, already_used_points, end_offset):
    min_dist_tuple = (float("inf"),None,None)
    if end_point:
        start_point = end_points_list[init_point_index]
    else:
        start_point = start_points_list[init_point_index]



    for point_index in range(len(start_points_list)):
        if not already_used_points[point_index]:
            distance = dist(start_point,start_points_list[point_index])
            if distance < min_dist_tuple[0] :
                min_dist_tuple = (distance,point_index, False)



    for point_index in range(len(end_points_list)):
        if not already_used_points[point_index]:
            distance = dist(start_point,end_points_list[point_index])
            if distance < min_dist_tuple[0] :
                min_dist_tuple = (distance,point_index + end_offset, True)



    return min_dist_tuple




def arrange_path_one_block(lines):
    dist_lists = [(float("inf"),None,None) for i in range(len(lines)*2)]
    start_points_list = [None]*len(lines)
    end_points_list = [None]*len(lines)
    for line_index in range(len(lines)):
        start_points_list[line_index] = lines[line_index][0]
        end_points_list[line_index] = lines[line_index][len(lines[line_index])-1]

    end_offset = len(lines) -1

    already_used_points = [False]*(len(lines)*2)

    for start_point_index in range(len(start_points_list)):
        start_point = start_points_list[start_point_index]


        for point_index in range(len(start_points_list)):
            if start_point_index != point_index:
                if not already_used_points[point_index]:
                    distance = dist(start_point,start_points_list[point_index])
                    if distance < dist_lists[start_point_index][0] :
                        dist_lists[start_point_index] = (distance,point_index, False)
                        used_point_index1 = point_index
                        used_point_index2 = point_index + end_offset


        for point_index in range(len(end_points_list)):
            if start_point_index != point_index:
                if not already_used_points[point_index]:
                    distance = dist(start_point,end_points_list[point_index])
                    if distance < dist_lists[start_point_index][0] :
                        dist_lists[start_point_index] = (distance,point_index + end_offset, True)
                        used_point_index1 = point_index
                        used_point_index2 = point_index + end_offset

        already_used_points[used_point_index1] = True
        already_used_points[used_point_index2] = True

    for end_point_index in range(len(end_points_list)):
        end_point = end_points_list[end_point_index]

        offseted_index = end_point_index + end_offset

        for point_index in range(len(start_points_list)):
            if end_point_index != point_index:
                if not already_used_points[point_index]:
                    distance = dist(end_point,start_points_list[point_index])
                    if distance < dist_lists[offseted_index][0] :
                        dist_lists[offseted_index] = (distance,point_index, False)
                        used_point_index1 = point_index
                        used_point_index2 = point_index + end_offset


        for point_index in range(len(end_points_list)):
            if end_point_index != point_index:
                if not already_used_points[point_index]:
                    distance = dist(end_point,end_points_list[point_index])
                    if distance < dist_lists[offseted_index][0] :
                        dist_lists[offseted_index] = (distance, point_index + end_offset, True)
                        used_point_index1 = point_index
                        used_point_index2 = point_index + end_offset

        already_used_points[used_point_index1] = True
        already_used_points[used_point_index2] = True


    ordered_lines = []
    current_index = 0
    end_point = True #the end point in the new referential is also an end point in the unordered referential



    while(len(ordered_lines)< len(lines)):


        if end_point:#search with begining point
            # reversed_list = lines[current_index]
            lines[current_index].reverse()
            ordered_lines.append(lines[current_index])
            next_point_tuple = dist_lists[current_index ]
        else: #search with end point
            ordered_lines.append(lines[current_index])
            next_point_tuple = dist_lists[current_index + end_offset]

        current_index = next_point_tuple[1] % len(lines)
        end_point = next_point_tuple[2]

    return ordered_lines





    # index = 0
    # max_index = len(lines)-1
    # while(index < max_index):
    #
    #     start_point = start_points_list.pop()
    #     end_point = end_points_list.pop()
    #     start_point_dists = dist_lists[index]
    #     index2 = index + len(lines)
    #     end_point_dists = dist_lists[index2]
    #     for point_index in range(len(start_points_list)):
    #         start_point_dists.set(dist(start_point,start_points_list[point_index]),index+point_index)
    #         end_point_dists.set(dist(end_point,start_points_list[point_index]),index+point_index)
    #
    #     for point_index in range(len(end_points_list)):
    #         start_point_dists.set(dist(start_point,end_points_list[point_index]),index2+point_index)
    #         end_point_dists.set(dist(end_point,end_points_list[point_index]),index2+point_index)


def dist(point1, point2):
    return pow((point1.x-point2.x),2) + pow((point1.y-point2.y),2)


def arrange_path_with_sorted_lists(lines):
    #todo: ordered list retrieval
    dist_lists = [bintrees.FastRBTree() for i in range(len(lines)*2)]
    start_points_list = [(float("inf"),None)]*len(lines)
    end_points_list = [(float("inf"),None)]*len(lines)
    for line_index in range(len(lines)):
        start_points_list[line_index] = lines[line_index][0]
        end_points_list[line_index] = lines[line_index][len(lines[line_index])-1]

    end_offset = len(lines) -1

    for start_point_index in range(len(start_points_list)):
        start_point = start_points_list[start_point_index]

        start_point_dists = dist_lists[start_point_index]

        for point_index in range(len(start_points_list)):
            if start_point_index != point_index:
                start_point_dists.insert(dist(start_point,start_points_list[point_index]),point_index)


        for point_index in range(len(end_points_list)):
            if start_point_index != point_index:
                start_point_dists.insert(dist(start_point,end_points_list[point_index]),end_offset + point_index)

    for start_point_index in range(len(start_points_list)):
        end_point = end_points_list[start_point_index]

        end_point_dists = dist_lists[start_point_index + end_offset]
        for point_index in range(len(start_points_list)):
            end_point_dists.insert(dist(end_point,start_points_list[point_index]),point_index)


        for point_index in range(len(end_points_list)):
            end_point_dists.insert(dist(end_point,end_points_list[point_index]),end_offset + point_index)

    # ordered_lines = []
    # first_point =  lines[0][len(lines[0])-1]
    # ordered_lines.append(lines[0])
    # while(len(ordered_lines)< len(lines)):
    #     iter = rbtree.iter(dist_lists[0] + end_offset)
    #     i.goto(0)
    #     next_point = i.item
    #     print(next_point)

