from slicer.island import Island
from slicer.Elements import Outline
from slicer.Polygon_stack import *
from slicer.Line_group import *
import slicer.config as config
from slicer.Line_stack import *
from slicer.utils import overlap

class Layer():

    def __init__(self, print_tree, layers, index, BBox, support_polylines = []):#layers are only passed as a reference to get an acces for skin processing
        self.print_tree = print_tree
        self.layers = layers
        self.islands = []
        self.index = index
        self.BBox = BBox
        if self.index == 0 and config.raft == True:
            config.line_width = 0.35
        self.process_islands()
        self.support_open_path, self.support_boundary_ps = support_polylines
        self.support_polylines = self.support_polygon_union_with_outline(support_polylines)
        config.reset()

    def get_raft_base(self):
        raft_base = Polygon_stack()
        for island in self.islands:
            raft_base = raft_base.union_with(island.get_raft_base())
        return raft_base

    def G_print(self):
        if self.index == 0 and config.raft == True:
            polylines = Line_group("contact_layer", False)

        else:
            polylines = Line_group("layer", False)

        if self.index == 0 and (config.platform_bound == "brim" or config.platform_bound == "skirts"):
            skirtPolylines = Line_group("skirt", True, config.line_width)
            skirts = Polygon_stack()
            for island in self.islands:
                skirts = skirts.union_with(island.get_platform_bound())
            if not self.support_boundary_ps.isEmpty:
                skirts = skirts.union_with(self.support_boundary_ps.offset(config.line_width*4))
            skirtPolylines.add_chains(skirts.get_print_line())
            for count in range(config.platform_bound_count):
                skirts = skirts.offset(config.line_width)
                skirtPolylines.add_chains(skirts.get_print_line())
            polylines.add_group(skirtPolylines)

        for island in self.islands:
            polylines.add_group(island.g_print())

        support_line_group = Line_group('support', True, config.line_width)
        for polyline in self.support_polylines:
            support_line_group.add_chain(polyline)
        polylines.add_group(support_line_group)

        return polylines

    def process_shells(self):
        for island in self.islands:
            island.process_shells()

    def process_skins(self):
        if self.index == 0 and config.raft == True:
            config.line_width = 0.35
        for island in self.islands:
            island.process_skins()
        config.reset()

    def prepare_skins(self):
        if self.index == 0 and config.raft == True:
            config.line_width = 0.35
        for island in self.islands:
            island.prepare_skins()
        config.reset()

    # def get_skins(self):
    #     skins = Polygon_stack()
    #     for island in self.islands:
    #         if island.skins is not None:
    #             skins.add_polygon_stack(island.skins.skins_as_polygon_stack)
    #     return skins

    def get_downskins(self):
        skins = Polygon_stack()
        for island in self.islands:
            if not island.downskins.isEmpty:
                skins.add_polygon_stack(island.downskins)
        return skins

    def get_upskins(self):
        skins = Polygon_stack()
        for island in self.islands:
            if not island.upskins.isEmpty:
                skins.add_polygon_stack(island.upskins)
        return skins

    def process_infill(self):
        if self.index == 0 and config.raft == True:
            config.line_width = 0.35
        for island in self.islands:
            island.process_infill()
        config.reset()


    def poly1_in_poly2(self,poly1,poly2):
        point = poly1[0]
        if pyclipper.PointInPolygon(point,poly2):
            return True
        else:
            return False

    def detect_islands(self):
        po = pyclipper.PyclipperOffset()
        po.MiterLimit = 2
        base = 1#pow(10, 15)
        empty_poly = Polygon_stack([[[base, base], [base + 1, base], [base + 1, base + 1], [base, base + 1]]])
        polys = pyclipper.PolyTreeToPaths(diff_layers_as_polytree(self.layers[self.index], empty_poly.polygons, True))
        po.AddPaths(polys, pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
        islandStack = Island_stack(po.Execute2(pyclipper.scale_to_clipper(-config.line_width/2)))
        return  islandStack.get_islands()




    def process_islands(self):
        if len(self.layers[self.index]) != 0:
            islands = self.detect_islands()
            for island in islands:
                pc = pyclipper.Pyclipper()

                isle = Island(self.print_tree,island, self.layers,self.index,self.BBox,self)
                self.islands.append(isle)

    def get_outline(self):
        ps = Polygon_stack()
        for island in self.islands:
            ps.add_polygons(island.get_outterbounds().polygons)
        return ps.union_self()

    def get_restricted_outline(self, bbox):
        ps = Polygon_stack()
        for island in self.islands:
            if overlap(island.obb, bbox):
                ps.add_polygons(island.get_outterbounds().polygons)
        return ps.union_self()

    def support_polygon_union_with_outline(self, support_polylines):

        outline = self.get_outline()
        offseted_outline = outline.offset(config.line_width)
        # offseted_outline = outline # testing

        polylines = []
        # polygons
        solution_polygons_ps = self.support_boundary_ps.difference_with(offseted_outline)
        polylines += solution_polygons_ps.get_print_line()

        # open_path
        # offseted_outline.visualize()
        solution_open_path_ls = self.support_open_path.difference_with(offseted_outline)
        polylines += solution_open_path_ls.get_print_line()

        # solution_open_path_ls.visualize()
        def distance(x, y):
            import numpy as np 
            x = np.array(x)
            y = np.array(y)
            return np.linalg.norm(x-y)
        from collections import namedtuple        

        if polylines != []:
            data_dict = [] # integer key: {start:,end:,line:}
            Line_Data = namedtuple('Line_Data', 'start end line')
            # print(len(polylines))
            for each_line in polylines:
                if len(each_line) >1:
                    data_dict.append(Line_Data(each_line[0], each_line[-1], each_line))

            # start at first element
            arranged_line = Line_stack() 
            # print(len(data_dict))
            first_line = data_dict.pop()
            end = pyclipper.scale_from_clipper(first_line.end)
            arranged_line.add_line(first_line.line)
            while data_dict:
                shortest_distance = 999999999999999
                delete_index = None
                for i in range(len(data_dict)):
                    start_point = pyclipper.scale_from_clipper(data_dict[i].start)
                    if distance(start_point, end) < shortest_distance:
                        shortest_distance = distance(start_point, end)
                        delete_index = i

                
                arranged_line.add_line(data_dict[delete_index].line)
                end = pyclipper.scale_from_clipper(data_dict[delete_index].end)
                del data_dict[delete_index]
            return arranged_line.lines
        return polylines

        # else:
        #     return []
