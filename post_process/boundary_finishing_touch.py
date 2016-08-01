
from slicer.post_process.path_planner import arrange_path
from slicer.post_process.Tree_task import Tree_task
from slicer.post_process.print_quality_optimizer import shorten_last_line, reorder_lines_close_to_point
import slicer.config.config as config

class Boundary_finish(Tree_task):

    def boundary(self, line_group):
        if config.boundary_starts_close_to_point != None:
            reorder_lines_close_to_point(config.boundary_starts_close_to_point, line_group)
        if config.coast_at_end_length > 0:
            shorten_last_line(line_group, config.coast_at_end_length)
    def inner_boundary(self, line_group):
        if config.boundary_starts_close_to_point != None:
            reorder_lines_close_to_point(config.boundary_starts_close_to_point, line_group)
        if config.coast_at_end_length > 0:
            shorten_last_line(line_group, config.coast_at_end_length)
        
