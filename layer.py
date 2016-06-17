from slicer.island import Island
from slicer.Elements import Outline
from slicer.Polygon_stack import *
from slicer.Line_group import *
import slicer.config as config

class Layer():

    def __init__(self, print_tree, layers, index, BBox, support_polylines = []):#layers are only passed as a reference to get an acces for skin processing
        self.print_tree = print_tree
        self.layers = layers
        self.islands = []
        self.index = index
        self.BBox = BBox
        self.process_islands()
        self.support_polylines = support_polylines

    def G_print(self):
        polylines = Line_group("layer")

        if self.index == 0:
            skirtPolylines = Line_group("skirt", config.line_width)
            skirts = Polygon_stack()
            for island in self.islands:
                skirts = skirts.union_with(island.get_platform_bound())
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



