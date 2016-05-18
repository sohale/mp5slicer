from Island import Island
import pyclipper
from Polynode import *
from utils import *
from Island_stack import *
from Elements import Outline
from Polygon_stack import *
from Line_group import *
from clipper_operations import union_layers_polytree
import config

class Layer():

    def __init__(self,print_tree, layers, index,BBox):#layers are only passed as a reference to get an acces for skin processing
        self.print_tree = print_tree
        self.layers = layers
        self.islands = []
        self.index = index
        self.BBox = BBox
        self.process_islands()

    def G_print(self):
        polylines = Line_group("layer")
        strikePolylines = Line_group("boundary",config.line_width)
        strikes = Polygon_stack()
        for island in self.islands:
            if self.index == 0:
                strikes.add_polygon_stack(island.get_strike())
            polylines.add_group(island.g_print())
        if self.index == 0:
            unionStrikes = union_layers_polytree(strikes.polygons,strikes.polygons,True)
            for strike in unionStrikes.Childs:
                strikePolylines.add_chain(Outline.process_polyline(strike.Contour))
            polylines.add_group(strikePolylines)
        return polylines

    def process_shells(self):
        for island in self.islands:
            island.process_shells()

    def process_skins(self):
        for island in self.islands:
            island.process_skins()

    def prepare_skins(self):
        for island in self.islands:
            island.prepare_skins()

    # def get_skins(self):
    #     skins = Polygon_stack()
    #     for island in self.islands:
    #         if island.skins is not None:
    #             skins.add_polygon_stack(island.skins.skins_as_polygon_stack)
    #     return skins

    def get_downskins(self):
        skins = Polygon_stack()
        for island in self.islands:
            if island.skins is not None:
                skins.add_polygon_stack(island.skins.downskins)
        return skins

    def get_upskins(self):
        skins = Polygon_stack()
        for island in self.islands:
            if island.skins is not None:
                skins.add_polygon_stack(island.skins.upskins)
        return skins

    def process_infill(self):
        for island in self.islands:
            island.process_infill()

    def poly1_in_poly2(self,poly1,poly2):
        point = poly1[0]
        if pyclipper.PointInPolygon(point,poly2):
            return True
        else:
            return False

    def detect_islands(self):
        po = pyclipper.PyclipperOffset()
        base = pow(10, 15)
        empty_poly = Polygon_stack([[[base, base], [base + 1, base], [base + 1, base + 1], [base, base + 1]]])
        polys = pyclipper.PolyTreeToPaths(diff_layers_as_polytree(self.layers[self.index], empty_poly.polygons, True))
        po.AddPaths(polys, pyclipper.JT_SQUARE, pyclipper.ET_CLOSEDPOLYGON)
        #offseted = Polygon_stack(po.Execute(pyclipper.scale_to_clipper(-config.line_width/2)))
        islandStack = Island_stack(po.Execute2(pyclipper.scale_to_clipper(-config.line_width/2)))
        #return offseted.split_in_islands()
        return  islandStack.get_islands()


    #DO NOT delete: this might be faster than detecting islands with pyclipper only
    # def detect_islands_old(self):
    #     islands = Polynode([])
    #     polygons = self.layers[self.index]
    #     # make a polynode for every polygon
    #     for poly_index in range(len(polygons)):
    #         islands.childs.append(Polynode(polygons[poly_index]))
    #     # make the three of polynodes
    #     for node1_index in range(len(islands.childs)):
    #         for node2_index in range(len(islands.childs)):
    #             if islands.childs[node1_index] != islands.childs[node2_index]:
    #                 if islands.childs[node1_index] != None and islands.childs[node2_index] != None:
    #                     if self.poly1_in_poly2(islands.childs[node1_index].contour,islands.childs[node2_index].contour):
    #                         # vizz_2d_multi([islands.childs[node1_index].contour,islands.childs[node2_index].contour])
    #                         islands.childs[node2_index].depth = max(islands.childs[node2_index].depth,islands.childs[node1_index].depth +1 )
    #                         islands.childs[node2_index].childs.append(islands.childs[node1_index])
    #                         islands.childs[node1_index] = None
    #     # split polynodes containing an island in multiple islands
    #     # for node_index in range(len(islands.childs)):
    #     #     if islands.childs[node1_index].depth > 1:
    #     #         #todo:split
    #     #         pass
    #     # remove every empty polynode
    #     i = 0
    #     while i < len( islands.childs):
    #         if islands.childs[i] == None:
    #             del islands.childs[i]
    #         else:
    #             i += 1
    #     return islands


    def process_islands(self):
        if len(self.layers[self.index]) != 0:
            islands = self.detect_islands()
            for island in islands:
                pc = pyclipper.Pyclipper()

                isle = Island(self.print_tree,island, self.layers,self.index,self.BBox,self)
                self.islands.append(isle)



