from gcode_writer import *
from Line_group import *

class G_buffer:
    layer_list = []
    filename= "tppt.gcode"

    def __init__(self):
        self.skip_retraction = False

    def add_layer(self,list):
        self.layer_list.append(list)


    def print_Gcode(self):
        printSettings = PrintSettings({})
        gcodeEnvironment = GCodeEnvironment(printSettings)
        # create the gcodefile
        gcodeFile = open(self.filename, "w+")
        gcodeFile.write("M109 S"+str(printSettings.temperature)+"\n")
        # gcodeFile.write("M207 S4 F30 Z0.5\n")
        # gcodeFile.write("M208 S0 F20\n")
        gcodeFile.write(gcodeEnvironment.startcode())

        # print two lines to extrude filament
        gcodeFile.write(gcodeEnvironment.goToNextPoint((0,0),True))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((180,0)))
        gcodeFile.write(gcodeEnvironment.goToNextPoint((180,2),True))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((0,2)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((0,4)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((180,4)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((180,6)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((10,6)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((10,10)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint((0,10)))



        def print_leaf(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        gcodeFile.write(gcodeEnvironment.drawToNextPoint(line[point_index]))

        def print_boundary(boundary):
            for line in boundary.sub_lines:
                if len(line) > 0:
                    gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0],True))
                    for point_index in range(1,len(line)):
                        gcodeFile.write(gcodeEnvironment.drawToNextPoint(line[point_index]))
            self.skip_retraction = False

        def print_infill(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        gcodeFile.write(gcodeEnvironment.drawToNextPoint(line[point_index], 4000))

        def print_skin(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        gcodeFile.write(gcodeEnvironment.drawToNextPoint(line[point_index], 3000))



        def switch_leaf(leaf):
            switch = {
                "skin": print_skin,
                "infill": print_infill,
                "hole": print_boundary,
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
            gcodeEnvironment.Z += printSettings.layerThickness

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



        gcodeFile.write(gcodeEnvironment.retractFilament(printSettings.retractionLength))
        gcodeFile.write(gcodeEnvironment.endcode())
        gcodeFile.close()

        print("GCode written")