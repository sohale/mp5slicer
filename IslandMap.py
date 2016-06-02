from IslandMapNode import IslandMapNode
import pyclipper
from IslandMapEdge import IslandMapEdge
from math import sqrt,pow

class IslandMap:

    def __init__(self, step,bound,holes,shells):
        """ initializes a graph object """
        self.__graph_dict = {}
        self.bound = bound
        self.holes = holes
        self.shells = shells
        self.step = step
        self.__generate_points_for_one_poly(bound)
        for hole in holes:
            self.__generate_points_for_one_poly(hole)

        #here self.points contains every point in the bound but out of the holes
        boundPoints = []
        #for i in range(0,len(bound)):

        #for every poly we need to find the intersected point and assocy it to an index in the poly

        #create edges between everypoints if they dont cross anny hole or bound

    def __generate_all_points(self):
        currentCost = 0
        #for i in range(len(self.bound)-1):

    def get_graph(self):
        return self.__graph_dict()


    def __generate_points_for_one_poly(self,poly):
        currentCost = 0
        currentPath = [poly[0]]
        self.__graph_dict[tuple(poly[0])] = IslandMapNode(poly[0],{},poly,0)
        self.__generate_direct_edges(poly[0])
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

                self.__graph_dict[tuple(poly[startIndex])].addNeighbour(
                    IslandMapEdge(poly[startIndex], poly[stopIndex], currentCost, currentPath),poly[stopIndex])

                if not tuple(poly[stopIndex]) in self.__graph_dict:
                    self.__graph_dict[tuple(poly[stopIndex])] = IslandMapNode(poly[stopIndex],{},poly,stopIndex)


                self.__graph_dict[tuple(poly[stopIndex])].addNeighbour(
                    IslandMapEdge(poly[stopIndex], poly[startIndex], currentCost, list(reversed(currentPath))), poly[startIndex])

                self.__generate_direct_edges(poly[stopIndex])
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
            if not tuple(poly[-1]) in self.__graph_dict:
                self.__graph_dict[tuple(poly[-1])] = IslandMapNode(poly[-1], {}, poly, len(poly)-1)


            self.__graph_dict[tuple(poly[-1])].addNeighbour(IslandMapEdge(poly[-1],poly[startIndex],currentCost,list(reversed(currentPath))),poly[startIndex])
            self.__graph_dict[tuple(poly[startIndex])].addNeighbour(IslandMapEdge(poly[startIndex], poly[-1], currentCost, currentPath),poly[-1])

            self.__graph_dict[tuple(poly[-1])].addNeighbour(IslandMapEdge(poly[-1], poly[0], tmpCost, [poly[-1], poly[0]]),poly[0])
            self.__graph_dict[tuple(poly[0])].addNeighbour(IslandMapEdge(poly[0], poly[-1], tmpCost, [poly[0], poly[-1]]),poly[-1])
            self.__generate_direct_edges(poly[-1])
        else:
            self.__graph_dict[tuple(poly[startIndex])].addNeighbour(
                IslandMapEdge(poly[startIndex], poly[0], currentCost, currentPath.append(poly[0])),poly[0])
            self.__graph_dict[tuple(poly[0])].addNeighbour(
                IslandMapEdge(poly[0], poly[startIndex], currentCost, list(reversed(currentPath))),poly[startIndex])


        #manage case where step too high


    def __getDistance(self,point0,point1):
        return sqrt(pow(point0[0] - point1[0], 2) + pow(point0[1] - point1[1], 2))

    def __generate_direct_edges(self,point):
        for graphPoint in self.__graph_dict.keys():
            if not (graphPoint[0] == point[0] and graphPoint[1] == point[1]):
                if(self.__check_direct_edge(graphPoint,point)):
                    dist = self.__getDistance(point, graphPoint)
                    self.__graph_dict[tuple(point)].addNeighbour(
                        IslandMapEdge(point, graphPoint, dist, [point, graphPoint]),graphPoint)
                    self.__graph_dict[graphPoint].addNeighbour(
                        IslandMapEdge(graphPoint, point, dist, [graphPoint,point]),point)


    def __check_direct_edge(self,point0,point1):
        #for testing
        point1 = pyclipper.scale_to_clipper(point1)
        point0 = pyclipper.scale_to_clipper(point0)
        self.bound = pyclipper.scale_to_clipper(self.bound)
        self.holes = pyclipper.scale_to_clipper(self.holes)
        #########
        pc = pyclipper.Pyclipper()
        pc.AddPath([point0, point1], pyclipper.PT_SUBJECT, False)
        pc.AddPath(self.bound, pyclipper.PT_CLIP, True)
        result = pyclipper.OpenPathsFromPolyTree(pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
        if len(result ) != 0:
            point1 = pyclipper.scale_from_clipper(point1)
            point0 = pyclipper.scale_from_clipper(point0)
            self.bound = pyclipper.scale_from_clipper(self.bound)
            self.holes = pyclipper.scale_from_clipper(self.holes)
            return False
        for poly in  self.holes:
            pc.Clear()
            pc.AddPath([point0,point1],pyclipper.PT_SUBJECT,False)
            pc.AddPath(poly,pyclipper.PT_CLIP,True)
            result = pyclipper.OpenPathsFromPolyTree(pc.Execute2(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD))
            if len(result) !=1 or result[0][0][0] != point0[0] or result[0][0][1] != point0[1] or result[0][1][0] != point1[0] or result[0][1][1] != point1[1]:
                # for testing
                point1 = pyclipper.scale_from_clipper(point1)
                point0 = pyclipper.scale_from_clipper(point0)
                self.holes = pyclipper.scale_from_clipper(self.holes)
                self.bound = pyclipper.scale_from_clipper(self.bound)
                #############
                return False
        # for testing
        point1 = pyclipper.scale_from_clipper(point1)
        point0 = pyclipper.scale_from_clipper(point0)
        self.bound = pyclipper.scale_from_clipper(self.bound)
        self.holes = pyclipper.scale_from_clipper(self.holes)
        #############
        return True

        # poly = pyclipper.scale_to_clipper([[1,2],[2,3],[1,4],[2,5],[3,5.5],[4,6],[5,5],[6,3],[4,3],[2,1]])
        # map = IslandMap(pyclipper.scale_to_clipper(10),poly,[],[])

#     poly = [[1.5, 4], [1, 9.5], [4, 9], [3.5, 11], [6.5, 10.5], [7.5, 10], [8, 9], [9, 8.5], [10.5, 8], [11.5, 7.5],
#             [12, 7], [10.5, 6], [12, 4.5], [9, 2], [8.5, 3], [8, 3.5], [7, 4], [6, 3.5], [5.5, 3], [3.5, 2]]
#
#
# holes = [[[3, 7.5], [4, 8], [4.5, 7.5], [6.5, 5], [4, 6], [3, 6.5]],
#          [[7, 8], [9, 7], [10, 5], [9, 3.5], [8, 5], [6, 4.5], [5.5, 5.5], [6, 7]]]
# start_time = time.time()
# # for i in range(1000):
# map = IslandMap(15, poly, holes, [])
# sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
# start_time = time.time()
# l = 0
# for i in range(1000):
#     l += i
# sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))