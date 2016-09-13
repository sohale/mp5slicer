from slicer.post_process.Tree_task import TreeTask
from slicer.post_process.print_quality_optimizer import shorten_last_line,\
    reorder_lines_close_to_point, retract_at_point_inside_boundary
import slicer.config.config as config

class BoundaryFinish(TreeTask):
    def __init__(self):
        super().__init__()
        self.last_point = None
        self.inner_boundary_last_points = None

    def boundary(self, line_group):
        reorder_lines_close_to_point(line_group,
            config.boundary_starts_close_to_point)

        shorten_last_line(line_group,
            config.outer_boundary_coast_at_end_length)

        retract_at_point_inside_boundary(line_group,
            self.inner_boundary_last_points)

    def inner_boundary(self, line_group):
        self.inner_boundary_last_points = []
        for lines in line_group.sub_lines:
            try:
                self.inner_boundary_last_points.append(lines[0])
            except IndexError:
                pass

            try:
                self.inner_boundary_last_points.append(lines[1])
            except IndexError:
                pass

            try:
                self.inner_boundary_last_points.append(lines[-1])
            except IndexError:
                pass

            try:
                self.inner_boundary_last_points.append(lines[-2])
            except IndexError:
                pass

            # for i in lines:
            #     self.inner_boundary_last_points.append(i)

        reorder_lines_close_to_point(line_group, 
            config.boundary_starts_close_to_point)

        shorten_last_line(line_group, 
            config.inner_boundary_coast_at_end_length)