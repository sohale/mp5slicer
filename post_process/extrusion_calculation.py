from slicer.post_process.print_quality_optimizer import calculE
from slicer.post_process.Tree_task import Tree_task

class Cal_extrusion(Tree_task):
    def leaf(self, line_group):
        def extrusion_on_each_line(each_line):
            E_list = []
            for start_point, end_point in zip(each_line, each_line[1:]):
                E_list.append(calculE(start_point, end_point))
            return E_list

        res = list(map(extrusion_on_each_line, line_group.sub_lines))
        print(line_group.sub_lines)
        print(res)
        line_group.E = res

