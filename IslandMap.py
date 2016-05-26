import IslandMapNode
import pyclipper

class IslandMap:

    def __init__(self, step,bound,holes,shells,xmax,xmin,ymax,ymin):
        """ initializes a graph object """
        self.__graph_dict = {}
        self.bound = bound
        self.holes = holes
        self.shells = shells
        self.horizontalLines = [[[xmin,y],[xmax,y]] for y in range(ymin,ymax,step) ]
        self.verticalLines = [[[x, ymin], [x, ymax]] for x in range(xmin, xmax, step)]

    def __generate_graph(self):
        start_point = IslandMapNode(self.bound[0],[],self.bound,0)
        self.__graph_dict[self.bound[0]] = start_point

    def __discover(self,pointNode):
        point = pointNode.position
        next_points = [[point[0]+self.step,point[1]],[point[0],point[1]+self.step],[point[0]-self.step,point[1]],[point[0],point[1]-self.step]]

        for next_point in next_points:
            if not next_point in self.__graph_dict:
                if pyclipper.PointInPolygon(next_point,self.bound): # check union
                    print "compute"

                else:
                    print 'not in bound // add point on poly + points on shells'