from slicer.island import Island
from slicer.Elements import Outline
from slicer.Polygon_stack import *
from slicer.Line_group import *
import slicer.config as config
from slicer.Line_stack import *

class Layer():

    def __init__(self, print_tree, layers, index, BBox, support_polylines = []):#layers are only passed as a reference to get an acces for skin processing
        self.print_tree = print_tree
        self.layers = layers
        self.islands = []
        self.index = index
        self.BBox = BBox
        self.process_islands()
        self.support_open_path, self.support_boundary_ps = support_polylines
        self.support_polylines = self.support_polygon_union_with_outline(support_polylines)
    def G_print(self):
        polylines = Line_group("layer")

        if self.index == 0:
            skirtPolylines = Line_group("skirt", config.line_width)
            skirts = Polygon_stack()
            for island in self.islands:
                skirts = skirts.union_with(island.get_platform_bound())
            if not self.support_boundary_ps.isEmpty:
                skirts = skirts.union_with(self.support_boundary_ps.offset(config.line_width))
            skirtPolylines.add_chains(skirts.get_print_line())
            for count in range(config.platform_bound_count):
                skirts = skirts.offset(config.line_width)
                skirtPolylines.add_chains(skirts.get_print_line())
            polylines.add_group(skirtPolylines)

        for island in self.islands:
            polylines.add_group(island.g_print())

        support_line_group = Line_group('support', config.line_width)
        for polyline in self.support_polylines:
            support_line_group.add_chain(polyline)
        polylines.add_group(support_line_group)

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

    def outline(self):
        ps = Polygon_stack()
        for island in self.islands:
            ps.add_polygons(island.get_outterbounds().polygons)
        return ps.union_self()

    def support_polygon_union_with_outline(self, support_polylines):

        outline = self.outline()
        # offseted_outline = outline.offset(config.line_width)
        offseted_outline = outline # testing

        polylines = []
        # polygons
        solution_polygons_ps = self.support_boundary_ps.difference_with(offseted_outline)
        polylines += solution_polygons_ps.get_print_line()

        # open_path
        # offseted_outline.visualize()
        solution_open_path_ls = Line_stack(self.support_open_path.difference_with(offseted_outline))
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
            for each_line in polylines:
                data_dict.append(Line_Data(each_line[0], each_line[-1], each_line))

            # start at first element
            arranged_line = Line_stack() 
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
            # arranged_line.visualize()
            return arranged_line.lines

        else:
            return []
