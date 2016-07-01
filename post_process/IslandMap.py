import pyclipper
from math import sqrt,pow
from queue import Queue

from slicer.post_process.IslandMapEdge import IslandMapEdge
from slicer.post_process.IslandMapNode import IslandMapNode


class IslandMap:

    def __init__(self, step,bound,holes,list_shells,lastPos = None):
        """ initializes a graph object """
        self.__graph_dict_outline = {}
        self.__list_graph_dict_shell = []
        self.lastPos = lastPos
        self.bound = bound
        self.holes = holes
        self.list_shells = list_shells
        self.step = step
        self.__generate_points_for_one_poly(bound,self.__graph_dict_outline)
        for hole in holes:
            self.__generate_points_for_one_poly(hole,self.__graph_dict_outline)
        for shells in list_shells:
            shells_graph = {}
            for shell in shells:
                self.__generate_points_for_one_poly(shell,shells_graph)
            self.__list_graph_dict_shell.append(shells_graph)

        #here self.points contains every point in the bound but out of the holes
        boundPoints = []
        #for i in range(0,len(bound)):

        #for every poly we need to find the intersected point and assocy it to an index in the poly

        #create edges between everypoints if they dont cross anny hole or bound

    def __generate_all_points(self):
        currentCost = 0
        #for i in range(len(self.bound)-1):

    def get_graph(self):
        return self.__graph_dict_outline


    def __generate_points_for_one_poly(self,poly,graph):
        currentCost = 0
        currentPath = [poly[0]]
        graph[tuple(poly[0])] = IslandMapNode(poly[0], {}, poly, 0)
        self.__generate_direct_edges(poly[0],graph)
        startIndex = 0;
        i = 1
        while i < len(poly):
            tmpCost = self.__getDistance(poly[i-1],poly[i])
            if(tmpCost + currentCost >= self.step):
                if(i-1 != startIndex):
                    stopIndex = i-1
                    i-=1
                else:
                    stopIndex = i
                    currentCost = tmpCost
                    currentPath = [poly[startIndex], poly[stopIndex]]
                    #i+=1

                graph[tuple(poly[startIndex])].addNeighbour(
                    IslandMapEdge(poly[startIndex], poly[stopIndex], currentCost, currentPath),poly[stopIndex])

                if not tuple(poly[stopIndex]) in self.__graph_dict_outline:
                    graph[tuple(poly[stopIndex])] = IslandMapNode(poly[stopIndex], {}, poly, stopIndex)


                graph[tuple(poly[stopIndex])].addNeighbour(
                    IslandMapEdge(poly[stopIndex], poly[startIndex], currentCost, list(reversed(currentPath))), poly[startIndex])

                self.__generate_direct_edges(poly[stopIndex],graph)
                currentCost = 0
                currentPath = [poly[stopIndex]]
                startIndex = stopIndex
                #create all direct edges
            else:
                currentCost+=tmpCost
                currentPath.append(poly[i])
            i+=1
        tmpCost = self.__getDistance(poly[0], poly[-1])
        if(tmpCost + currentCost >= self.step):
            if not tuple(poly[-1]) in self.__graph_dict_outline:
                graph[tuple(poly[-1])] = IslandMapNode(poly[-1], {}, poly, len(poly) - 1)


            graph[tuple(poly[-1])].addNeighbour(IslandMapEdge(poly[-1], poly[startIndex], currentCost, list(reversed(currentPath))), poly[startIndex])
            graph[tuple(poly[startIndex])].addNeighbour(IslandMapEdge(poly[startIndex], poly[-1], currentCost, currentPath), poly[-1])

            graph[tuple(poly[-1])].addNeighbour(IslandMapEdge(poly[-1], poly[0], tmpCost, [poly[-1], poly[0]]), poly[0])
            graph[tuple(poly[0])].addNeighbour(IslandMapEdge(poly[0], poly[-1], tmpCost, [poly[0], poly[-1]]), poly[-1])
            self.__generate_direct_edges(poly[-1],graph)
        else:
            currentPath.append(poly[0])
            graph[tuple(poly[startIndex])].addNeighbour(
                IslandMapEdge(poly[startIndex], poly[0], currentCost,currentPath ),poly[0])
            graph[tuple(poly[0])].addNeighbour(
                IslandMapEdge(poly[0], poly[startIndex], currentCost, list(reversed(currentPath))),poly[startIndex])


        #TODO : manage case where step too high


    def __getDistance(self,point0,point1):
        return sqrt(pow(point0[0] - point1[0], 2) + pow(point0[1] - point1[1], 2))

    def __generate_direct_edges(self,point,graph):
        for graphPoint in graph.keys():
            if not (graphPoint[0] == point[0] and graphPoint[1] == point[1]):
                if(self.__check_direct_edge(graphPoint,point)):
                    dist = self.__getDistance(point, graphPoint)
                    graph[tuple(point)].addNeighbour(
                        IslandMapEdge(point, graphPoint, dist, [point, graphPoint]),graphPoint)
                    graph[graphPoint].addNeighbour(
                        IslandMapEdge(graphPoint, point, dist, [graphPoint,point]),point)


    def __check_direct_edge(self,point0,point1):

        pc = pyclipper.Pyclipper()
        pc.AddPath([point0, point1], pyclipper.PT_SUBJECT, False)
        pc.AddPath(self.bound, pyclipper.PT_CLIP, True)
        result = pyclipper.OpenPathsFromPolyTree(pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
        if len(result ) != 0:

            return False
        for poly in  self.holes:
            pc.Clear()
            pc.AddPath([point0,point1],pyclipper.PT_SUBJECT,False)
            pc.AddPath(poly,pyclipper.PT_CLIP,True)
            result = pyclipper.OpenPathsFromPolyTree(pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
            if len(result) !=1 or result[0][0][0] != point0[0] or result[0][0][1] != point0[1] or result[0][1][0] != point1[0] or result[0][1][1] != point1[1]:

                return False

        return True

    def dijkstra(self,graph, start, target,polygons):
        visited = {tuple(start): (0,[start])}
        node_queue = Queue(-1)
        node_queue.put(start)
        closest_polygon = (None,0,None) #(polygone,cost,node)

        while not node_queue.empty():
            node = node_queue.get()
            currentCost = visited[tuple(node)][0]
            currentPath = visited[tuple(node)][1]
            neighboors_dict = graph[tuple(node)].getNeighbours()
            for neighboor in neighboors_dict.keys():
                nextCost = currentCost + neighboors_dict[neighboor].cost
                if (closest_polygon[0] == None) or nextCost < closest_polygon[1] :
                    if (not neighboor in visited):
                        node_queue.put(neighboor)
                        visited[neighboor] = (nextCost,currentPath + neighboors_dict[neighboor].path[1:])
                    elif visited[neighboor][0] > nextCost:
                        visited[neighboor] = (nextCost, currentPath + neighboors_dict[neighboor].path[1:])
                    for polygon in polygons:
                        if polygon == graph[neighboor].poly:
                            closest_polygon = (polygon,nextCost,neighboor)
                            break
        if closest_polygon[0] != None:
            return  (visited[closest_polygon[2]][1],closest_polygon[0])

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
#         map.dijkstra(map.get_graph(), pyclipper.scale_to_clipper([1.5, 4]), 12, holes)
# sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
# start_time = time.time()
# l = 0
# for i in range(1000):
#     l += i
# sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
