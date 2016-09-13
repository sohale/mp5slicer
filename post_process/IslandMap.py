import pyclipper
from queue import Queue
from slicer.commons.utils import distance as calulate_distance

from slicer.post_process.IslandMapEdge import IslandMapEdge
from slicer.post_process.IslandMapNode import IslandMapNode

class IslandMap(object):

    def __init__(self, step, bound, holes, list_shells, last_pos=None):
        """ initializes a graph object """
        self.__graph_dict_outline = {}
        self.__list_graph_dict_shell = []
        self.last_pos = last_pos
        self.bound = bound
        self.holes = holes
        self.list_shells = list_shells
        self.step = step
        self.__generate_points_for_one_poly(bound, self.__graph_dict_outline)
        for hole in holes:
            self.__generate_points_for_one_poly(hole,
                                                self.__graph_dict_outline)
        for shells in list_shells:
            shells_graph = {}
            for shell in shells:
                self.__generate_points_for_one_poly(shell, shells_graph)
            self.__list_graph_dict_shell.append(shells_graph)

        # here self.points contains every point in the bound 
        # but out of the holes

        # for every poly we need to find the intersected point and 
        # assocy it to an index in the poly

        # create edges between everypoints if they dont cross anny hole
        # or bound

    def __generate_all_points(self):
        # currentCost = 0
        #for i in range(len(self.bound)-1):
        pass

    def get_graph(self):
        return self.__graph_dict_outline


    def __generate_points_for_one_poly(self, poly, graph):
        current_cost = 0
        current_path = [poly[0]]
        graph[tuple(poly[0])] = IslandMapNode(poly[0], {}, poly, 0)
        self.__generate_direct_edges(poly[0], graph)
        start_index = 0
        i = 1
        while i < len(poly):
            tmp_cost = calulate_distance(poly[i-1], poly[i])
            if tmp_cost + current_cost >= self.step:
                if i-1 != start_index:
                    stop_index = i-1
                    i -= 1
                else:
                    stop_index = i
                    current_cost = tmp_cost
                    current_path = [poly[start_index], poly[stop_index]]
                    #i+=1

                graph[tuple(poly[start_index])].add_neighbour(
                    IslandMapEdge(poly[start_index], 
                                  poly[stop_index], 
                                  current_cost, current_path),
                    poly[stop_index])

                if tuple(poly[stop_index]) not in self.__graph_dict_outline:
                    graph[tuple(poly[stop_index])] = IslandMapNode(poly[stop_index],
                                                                   {},
                                                                   poly,
                                                                   stop_index)


                graph[tuple(poly[stop_index])].add_neighbour(
                    IslandMapEdge(poly[stop_index],
                                  poly[start_index],
                                  current_cost,
                                  list(reversed(current_path))),
                    poly[start_index])

                self.__generate_direct_edges(poly[stop_index], graph)
                current_cost = 0
                current_path = [poly[stop_index]]
                start_index = stop_index
                #create all direct edges
            else:
                current_cost += tmp_cost
                current_path.append(poly[i])
            i += 1
        tmp_cost = calulate_distance(poly[0], poly[-1])
        if tmp_cost + current_cost >= self.step:
            if tuple(poly[-1]) not in self.__graph_dict_outline:
                graph[tuple(poly[-1])] = IslandMapNode(poly[-1],
                                                       {},
                                                       poly,
                                                       len(poly) - 1)


            graph[tuple(poly[-1])].add_neighbour(
                IslandMapEdge(poly[-1],
                              poly[start_index],
                              current_cost,
                              list(reversed(current_path))),
                poly[start_index])

            graph[tuple(poly[start_index])].add_neighbour(
                IslandMapEdge(poly[start_index],
                              poly[-1],
                              current_cost,
                              current_path),
                poly[-1])

            graph[tuple(poly[-1])].add_neighbour(
                IslandMapEdge(poly[-1],
                              poly[0],
                              tmp_cost,
                              [poly[-1], poly[0]]),
                poly[0])

            graph[tuple(poly[0])].add_neighbour(
                IslandMapEdge(poly[0],
                              poly[-1],
                              tmp_cost,
                              [poly[0], poly[-1]]),
                poly[-1])

            self.__generate_direct_edges(poly[-1], graph)
        else:
            current_path.append(poly[0])
            graph[tuple(poly[start_index])].add_neighbour(
                IslandMapEdge(poly[start_index],
                              poly[0],
                              current_cost,
                              current_path),
                poly[0])
            graph[tuple(poly[0])].add_neighbour(
                IslandMapEdge(poly[0],
                              poly[start_index],
                              current_cost,
                              list(reversed(current_path))),
                poly[start_index])


        #TODO : manage case where step too high

    def __generate_direct_edges(self, point, graph):
        for graph_point in graph.keys():
            if not (graph_point[0] == point[0] and graph_point[1] == point[1]):
                if self.__check_direct_edge(graph_point, point):
                    dist = calulate_distance(point, graph_point)
                    graph[tuple(point)].add_neighbour(
                        IslandMapEdge(point,
                                      graph_point,
                                      dist,
                                      [point, graph_point]),
                        graph_point)
                    graph[graph_point].add_neighbour(
                        IslandMapEdge(graph_point,
                                      point,
                                      dist,
                                      [graph_point, point]),
                        point)


    def __check_direct_edge(self, point0, point1):

        pc = pyclipper.Pyclipper()
        pc.AddPath([point0, point1], pyclipper.PT_SUBJECT, False)
        pc.AddPath(self.bound, pyclipper.PT_CLIP, True)
        result = pyclipper.OpenPathsFromPolyTree(
            pc.Execute2(pyclipper.CT_DIFFERENCE,
                        pyclipper.PFT_EVENODD,
                        pyclipper.PFT_EVENODD))
        if len(result) != 0:
            return False
        for poly in  self.holes:
            pc.Clear()
            pc.AddPath([point0, point1], pyclipper.PT_SUBJECT, False)
            pc.AddPath(poly, pyclipper.PT_CLIP, True)
            result = pyclipper.OpenPathsFromPolyTree(
                pc.Execute2(pyclipper.CT_DIFFERENCE,
                            pyclipper.PFT_EVENODD,
                            pyclipper.PFT_EVENODD))

            if len(result) != 1 or \
                result[0][0][0] != point0[0] or\
                result[0][0][1] != point0[1] or\
                result[0][1][0] != point1[0] or\
                result[0][1][1] != point1[1]:

                return False

        return True

    @staticmethod
    def dijkstra(graph, start, polygons):
        visited = {tuple(start): (0, [start])}
        node_queue = Queue(-1)
        node_queue.put(start)
        closest_polygon = (None, 0, None) #(polygone,cost,node)

        while not node_queue.empty():
            node = node_queue.get()
            current_cost = visited[tuple(node)][0]
            current_path = visited[tuple(node)][1]
            neighboors_dict = graph[tuple(node)].get_neighbours()
            for neighboor in neighboors_dict.keys():
                next_cost = current_cost + neighboors_dict[neighboor].cost
                if (closest_polygon[0] is None) or \
                        next_cost < closest_polygon[1]:
                    if not neighboor in visited:
                        node_queue.put(neighboor)
                        visited[neighboor] = (next_cost, 
                            current_path+neighboors_dict[neighboor].path[1:])
                    elif visited[neighboor][0] > next_cost:
                        visited[neighboor] = (next_cost,
                            current_path+neighboors_dict[neighboor].path[1:])
                    for polygon in polygons:
                        if polygon == graph[neighboor].poly:
                            closest_polygon = (polygon, next_cost, neighboor)
                            break
        if closest_polygon[0] != None:
            return  (visited[closest_polygon[2]][1], closest_polygon[0])

        return None

#         poly = pyclipper.scale_to_clipper(
#             [[1.5, 4], [1, 9.5], [4, 9], [3.5, 11], [6.5, 10.5], [7.5, 10], [8, 9], [9, 8.5], [10.5, 8], [11.5, 7.5],
#              [12, 7], [10.5, 6], [12, 4.5], [9, 2], [8.5, 3], [8, 3.5], [7, 4], [6, 3.5], [5.5, 3], [3.5, 2]])
#
#
# holes = pyclipper.scale_to_clipper([[[3, 7.5], [4, 8], [4.5, 7.5], [6.5, 5], [4, 6], [3, 6.5]],
#                                     [[7, 8], [9, 7], [10, 5], [9, 3.5], [8, 5], [6, 4.5], [5.5, 5.5], [6, 7]]])
# start_time = time.time()
# for i in range(300):
#     map = IslandMap(1, poly, holes, [])
#     for j in range(30):
#         map.dijkstra(map.get_graph(), pyclipper.scale_to_clipper([1.5, 4]), holes)
# sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
# start_time = time.time()
# l = 0
# for i in range(1000):
#     l += i
# sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
