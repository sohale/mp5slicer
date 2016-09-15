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
            config.BOUNDARY_STARTS_CLOSE_TO_POINT)

        shorten_last_line(line_group,
            config.OUTER_BOUNDARY_COAST_AT_END_LENGTH)

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
            config.BOUNDARY_STARTS_CLOSE_TO_POINT)

        shorten_last_line(line_group,
            config.INNER_BOUNDARY_COAST_AT_END_LENGTH)
