import slicer.config.config as config
from slicer.commons.utils import overlap, does_bounding_box_intersect, scale_value_to_clipper
from slicer.print_tree.Line_group import *
from slicer.print_tree.Line_stack import *
from slicer.print_tree.island import Island
import numpy as np

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


        if config.useSupport:
            self.support_open_path, self.support_boundary_ps = support_polylines
        else:
            self.support_open_path, self.support_boundary_ps = Line_stack(), Polygon_stack()

        # self.support_line_stack = support_polylines[0]
        # self.support_polylines = self.support_polygon_difference_with_outline(support_polylines)
        config.reset()

        # support
        self.this_layer_support_area = None
        self.aggregated_support_area = None

    def get_this_layer_support_area(self): # prepare support
        this_layer_index = self.index
        if this_layer_index != 0:
            one_below_layer_index = self.index - 1
        else: # layer_index == 0
            return None

        this_layer_outline = Polygon_stack(self.layers[this_layer_index])
        offset_value = config.layerThickness*np.tan(np.radians(config.supportOverhangangle))
        assert offset_value >= 0

        offseted_one_last_ps = Polygon_stack(self.layers[one_below_layer_index]).offset(offset_value)
        # offseted_one_last_ps = offseted_one_last_ps.remove_small_polygons(5)
        # old
        this_layer_support_required_ps = this_layer_outline.difference_with(offseted_one_last_ps)
        this_layer_support_required_ps = this_layer_support_required_ps.offset(config.support_area_enlarge_value) # think about the number
        self.this_layer_support_area = this_layer_support_required_ps
    

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
            if config.platform_bound == "skirts" and not self.support_boundary_ps.is_empty():
                    skirts = skirts.union_with(self.support_boundary_ps.offset(config.line_width*3))
                    # self.support_open_path.difference_with(skirts)
                    # pass
            elif config.platform_bound == "brim" and not self.support_boundary_ps.is_empty():
                    skirts = skirts.union_with(self.support_boundary_ps.offset(0))
                    # self.support_open_path.difference_with(skirts)
                    # pass

            else:
                pass
                # raise NotImplementedError

            skirts_all = [skirts]        
            for count in range(config.platform_bound_count):
                skirts = skirts.offset(config.line_width)
                skirts_all.append(skirts)
            # self.support_open_path = self.support_open_path.difference_with(skirts)
            
            for skirts in skirts_all[::-1]:# reverse order from outside to inside
                skirtPolylines.add_chains(skirts.get_print_line())
            polylines.add_group(skirtPolylines)

        for island in self.islands:
            polylines.add_group(island.g_print())

        support_line_group = Line_group('support', True, config.line_width)

        self.support_polylines = self.support_polygon_difference_with_outline()
        # self.support_polylines = self.support_line_stack.get_print_line()

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

    def prepare_support(self):
        self.detect_support_area = self.layers[self.index]
    # def get_skins(self):
    #     skins = Polygon_stack()
    #     for island in self.islands:
    #         if island.skins is not None:
    #             skins.add_polygon_stack(island.skins.skins_as_polygon_stack)
    #     return skins

    def get_downskins(self):
        skins = Polygon_stack()
        for island in self.islands:
            if not island.downskins.is_empty():
                skins.add_polygon_stack(island.downskins)
        return skins

    def get_upskins(self):
        skins = Polygon_stack()
        for island in self.islands:
            if not island.upskins.is_empty():
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
        islandStack = Island_stack(po.Execute2(scale_value_to_clipper(-config.line_width/2)))
        return  islandStack.get_islands()




    def process_islands(self):
        if len(self.layers[self.index]) != 0:
            islands = self.detect_islands()
            for island in islands:
                # pc = pyclipper.Pyclipper()

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
            if overlap(island.island_bbox, bbox):
                ps.add_polygons(island.get_outterbounds().polygons)
        return ps.union_self()

    def support_polygon_difference_with_outline(self):

        outline = self.get_outline()
        offseted_outline = outline.offset(config.support_horizontal_offset_from_parts)

        polylines = []

        # polygons
        solution_polygons_ps = self.support_boundary_ps.difference_with(offseted_outline)
        polylines += solution_polygons_ps.get_print_line()

        # open_path
        solution_open_path_ls = self.support_open_path.difference_with(offseted_outline)
        polylines += solution_open_path_ls.get_print_line()

        return polylines
