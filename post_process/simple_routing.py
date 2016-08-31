
from slicer.post_process.path_planner import arrange_path
from slicer.post_process.Tree_task import Tree_task

class Simple_router(Tree_task):

    def support(self, line_group):
        arrange_path(line_group)

    def infill(self, line_group):
        arrange_path(line_group)