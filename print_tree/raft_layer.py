import mp5slicer.config.config as config
from mp5slicer.post_process.path_planner import *
from mp5slicer.print_tree.Line_stack import *
from mp5slicer.print_tree.infill_paterns import *
from mp5slicer.commons.utils import scale_line_to_clipper

class RaftLayer(object):

    def __init__(self, is_top_raft, is_bottom_raft, bounding_box, polygons):
        self.BBox = bounding_box
        self.polygons = polygons
        self.is_top_raft = is_top_raft
        self.is_bottom_raft = is_bottom_raft

    def G_print(self):
        polylines = LineGroup("raft_layer", False)
        if self.is_top_raft:
            raft_polylines = LineGroup("top_raft", True, config.LINE_WIDTH)
        # elif self.is_bottom_raft:
        #     raft_polylines = LineGroup("bottom_raft", True, config.LINE_WIDTH)
        else:
            raft_polylines = LineGroup("raft", True, config.LINE_WIDTH)

        polylines.add_group(raft_polylines)

        x_or_y = False

        if self.is_bottom_raft:
            linear_infill_result = linear_infill2(config.LINE_WIDTH,
                                                  135,
                                                  self.BBox)

            infill_pattern = LineStack(scale_line_to_clipper(linear_infill_result))
        else:
            linear_infill_result = linear_infill2(config.LINE_WIDTH*2,
                                                  135,
                                                  self.BBox)

            infill_pattern = LineStack(scale_line_to_clipper(linear_infill_result))

        infill = LineStack(infill_pattern.intersect_with(self.polygons))
        raft_polylines.add_chains(infill.get_print_line())
        raft_polylines.add_chains(self.polygons.get_print_line())
        return polylines
