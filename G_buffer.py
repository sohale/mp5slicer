from gcode_writer import *
from Line_group import *
import config
import sys
import printer_config

class G_buffer:
    layer_list = []



    def __init__(self,to_file, gcode_filename = ""):
        self.to_file = to_file
        self.gcode_filename = gcode_filename
        self.skip_retraction = False

    def add_layer(self,list):
        self.layer_list.append(list)




    def print_Gcode(self):
        gcodeEnvironment = GCodeEnvironment()
        # create the gcode_output
        if self.to_file:
            gcode_output = open(self.gcode_filename, "w+")
        else:
            gcode_output = sys.stdout


        gcode_output.write(gcodeEnvironment.startcode(printer_config.model))




        def print_leaf(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        gcode_output.write(gcodeEnvironment.drawToNextPoint(line[point_index]))

        def print_boundary(boundary):
            for line in boundary.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],True))
                    for point_index in range(1,len(line)):
                        gcode_output.write(gcodeEnvironment.drawToNextPoint(line[point_index],config.boundarySpeed))
            self.skip_retraction = False

        def print_hole(boundary):
            for line in boundary.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        gcode_output.write(gcodeEnvironment.drawToNextPoint(line[point_index], config.holeSpeed))
            self.skip_retraction = False

        def print_infill(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        gcode_output.write(gcodeEnvironment.drawToNextPoint(line[point_index], config.infillSpeed))

        def print_skin(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        gcode_output.write(gcodeEnvironment.drawToNextPoint(line[point_index], config.skinSpeed))

        def print_inner_shell(shell):
            for line in shell.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        gcode_output.write(gcodeEnvironment.drawToNextPoint(line[point_index],config.shellSpeed))
            self.skip_retraction = False

        def switch_leaf(leaf):
            switch = {
                "skin": print_skin,
                "infill": print_infill,
                "hole": print_hole,
                "inner_boundary" : print_inner_shell,
                "inner_hole": print_inner_shell,
                "boundary": print_boundary
            }
            switch[leaf.type](leaf)

        def swith_node(node):
            switch = {
                "outline": print_node,
                "layer": print_layer,
                "island": print_node,
            }
            switch[node.type](node)

        def print_layer(node):

            for node in node.sub_lines:
                gotroughgroup(node)
            gcodeEnvironment.Z += config.layerThickness

        def print_node(node):
            for node in node.sub_lines:
                gotroughgroup(node)


        def gotroughgroup(group):
            if (group.isLeaf):
                switch_leaf(group)
            else:
                swith_node(group)

        for layer in self.layer_list:
            if len(layer.sub_lines) != 0:
                gotroughgroup(layer)



        gcode_output.write(gcodeEnvironment.retractFilament(config.retractionLength))
        gcode_output.write(gcodeEnvironment.endcode(printer_config.model))
        gcode_output.close()

        sys.stderr.write("GCode written")
