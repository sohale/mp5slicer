from slicer.post_process.path_planner import arrange_path
from slicer.post_process.Tree_task import TreeTask

class SimpleRouter(TreeTask):

    def support(self, line_group):
        arrange_path(line_group)

    def infill(self, line_group):
        arrange_path(line_group)

    def raft(self, line_group):
        arrange_path(line_group)

    def skin(self, line_group):
        arrange_path(line_group)
