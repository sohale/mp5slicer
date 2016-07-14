
from slicer.post_process.path_planner import arrange_path
from slicer.post_process.Tree_task import Tree_task
from slicer.post_process.print_quality_optimizer import shorten_last_line

class Boundary_finish(Tree_task):

    def boundary(self, line_group):
        shorten_last_line(line_group, 1)

    def inner_boundary(self, line_group):
        shorten_last_line(line_group, 1)