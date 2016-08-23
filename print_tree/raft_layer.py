import slicer.config.config as config
from slicer.post_process.path_planner import *
from slicer.print_tree.Line_stack import *
from slicer.print_tree.infill_paterns import *
from slicer.commons.utils import scale_line_to_clipper

class Raft_layer():

    def __init__(self,is_top_raft,is_bottom_raft, BBox, polygons):
        self.BBox = BBox
        self.polygons = polygons
        self.is_top_raft = is_top_raft
        self.is_bottom_raft = is_bottom_raft


    def G_print(self):
        polylines = Line_group("raft_layer", False)
        if self.is_top_raft:
            raft_polylines = Line_group("top_raft", True, config.line_width)
        # elif self.is_bottom_raft:
        #     raft_polylines = Line_group("bottom_raft", True, config.line_width)
        else:
            raft_polylines = Line_group("raft", True, config.line_width)

        polylines.add_group(raft_polylines)
        XorY = False
        if self.is_bottom_raft:
            infill_pattern = Line_stack(scale_line_to_clipper(linear_infill2(config.line_width,135,self.BBox)))
        else:
            infill_pattern = Line_stack(scale_line_to_clipper(linear_infill2(config.line_width * 2, 135, self.BBox)))
        infill = Line_stack(infill_pattern.intersect_with(self.polygons))
        raft_polylines.add_chains(infill.get_print_line())
        arrange_path(raft_polylines)
        raft_polylines.add_chains(self.polygons.get_print_line())
        return polylines