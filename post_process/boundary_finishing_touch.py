
from slicer.post_process.path_planner import arrange_path
from slicer.post_process.Tree_task import Tree_task
from slicer.post_process.print_quality_optimizer import shorten_last_line, reorder_lines_close_to_point, retract_at_point_inside_boundary
import slicer.config.config as config

class Boundary_finish(Tree_task):
    def __init__(self):
        self.last_point = None

    def boundary(self, line_group):
        reorder_lines_close_to_point(line_group, config.boundary_starts_close_to_point)
        shorten_last_line(line_group, config.outer_boundary_coast_at_end_length)
        retract_at_point_inside_boundary(line_group, self.last_point)

    def inner_boundary(self, line_group):
        reorder_lines_close_to_point(line_group, config.boundary_starts_close_to_point)
        shorten_last_line(line_group, config.inner_boundary_coast_at_end_length)
        try:
            self.last_point = line_group.sub_lines[0][0]
        except IndexError: # sub_lines empty
            self.last_point = None
