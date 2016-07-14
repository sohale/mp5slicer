from slicer.post_process.print_quality_optimizer import calculE
from slicer.post_process.Tree_task import Tree_task

class Cal_extrusion(Tree_task):
    def leaf(self, line_group):
        def extrusion_on_each_line(each_line):
            E_list = []
            print(len(each_line))
            if len(each_line) >= 2:
                for start_point, end_point in zip(each_line, each_line[1:]):
                    E_list.append(calculE(start_point, end_point))
            elif len(each_line) == 1:
                print('here')
                E_list.append(0)
                raise Tiger
            elif len(each_line) == 0:
                pass
            else:
                raise StandardError("this should not happend ever")
            return E_list

        res = list(map(extrusion_on_each_line, line_group.sub_lines))
        print('--------------------')
        print(line_group.sub_lines)
        line_group.E = res
        print(line_group.E)
        print(len(line_group.sub_lines))
        print(len(line_group.E))


