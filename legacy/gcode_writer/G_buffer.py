import sys
from .gcode_writer import GCodeEnvironment
import slicer.config.config as config
import slicer.config.printer_config as printer_config


class G_buffer:
    layer_list = []



    def __init__(self,to_file, gcode_filename = "", layerThickness_list = []):
        self.to_file = to_file
        self.gcode_filename = gcode_filename
        self.skip_retraction = False
        self.layer_index = 0
        self.previousPos = None
        self.layerIslands = None
        self.layerThickness_list = layerThickness_list 

    def add_layer_list(self,list):
        self.layer_list = list



    def print_Gcode(self):
        gcodeEnvironment = GCodeEnvironment()
        # create the gcode_output
        if self.to_file:
            gcode_output = open(self.gcode_filename, "w+")
        else:
            gcode_output = sys.stdout

        instruction = gcodeEnvironment.startcode(printer_config.model)
        instruction += "G1 F200 E" + str(config.initial_extrusion)
        gcode_output.write(instruction)

        # @profile
        def print_boundary(boundary):
            line_count = 0
            for line in boundary.sub_lines:
                point_in_each_line_counter = 0
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],True))
                    # for point_index in range(1,len(line)-1):
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.layerThickness, config.boundarySpeed, config.exteriorFanSpeed)
                        gcode_output.write(instruction)
                    # gcode_output.write(gcodeEnvironment.goToNextPoint(line[-1],True))
                        point_in_each_line_counter += 1
                line_count += 1
            self.skip_retraction = False

        # @profile
        def print_hole(boundary):
            for line in boundary.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.layerThickness, config.holeSpeed, config.exteriorFanSpeed)
                        gcode_output.write(instruction)
            self.skip_retraction = False

        # @profile
        def print_infill(infill):
            for line in infill.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        dist = gcodeEnvironment.calculDis(line[0])
                        if dist < config.line_width * 2.5:
                            instruction = gcodeEnvironment.drawToNextPoint(line[0], config.layerThickness,
                                                             config.infillSpeed, config.interiorFanSpeed)
                            gcode_output.write(instruction)
                        else:
                            gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                            self.skip_retraction = False
                    else:
                        dist = gcodeEnvironment.calculDis(line[0])
                        if dist < config.line_width * 2.5:
                            instruction = gcodeEnvironment.drawToNextPoint(line[0], config.layerThickness,
                                                             config.infillSpeed, config.interiorFanSpeed)
                            gcode_output.write(instruction)
                        else:
                            gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.layerThickness, config.infillSpeed, config.interiorFanSpeed)
                        gcode_output.write(instruction)

        # @profile
        def print_skin(skin):
            for line in skin.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        dist = gcodeEnvironment.calculDis(line[0])
                        if dist < config.line_width * 2.5:
                            instruction = gcodeEnvironment.drawToNextPoint(line[0], config.layerThickness,
                                                             config.infillSpeed, config.interiorFanSpeed)
                            gcode_output.write(instruction)
                        else:
                            gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                            self.skip_retraction = False
                    else:
                        dist = gcodeEnvironment.calculDis(line[0])
                        if dist < config.line_width * 2.5:
                            instruction = gcodeEnvironment.drawToNextPoint(line[0], config.layerThickness,
                                                             config.infillSpeed, config.interiorFanSpeed)
                            gcode_output.write(instruction)
                        else:
                            gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.layerThickness , config.skinSpeed, config.interiorFanSpeed)
                        gcode_output.write(instruction)

        def print_support(support):
            for line in support.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.layerThickness, config.supportSpeed, config.supportFanSpeed)
                        gcode_output.write(instruction)
            self.skip_retraction = False

        def print_inner_shell(shell):
            for line in shell.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],True))
                    for point_index in range(1,len(line)-1):
                    # for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.layerThickness, config.boundarySpeed, config.exteriorFanSpeed)
                        gcode_output.write(instruction)
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[-1],True))

            self.skip_retraction = False

        def print_skirt(skirt):
            for line in skirt.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.layerThickness, config.raftSpeed, 0.2)
                        gcode_output.write(instruction)
                        self.previousPos = line[point_index]
            self.skip_retraction = False

        def print_raft(raft):
            for line in raft.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], config.raftLayerThickness, config.raftSpeed, 0)
                        gcode_output.write(instruction)
                        self.previousPos = line[point_index]
            self.skip_retraction = False

        def print_top_raft(raft):
            config.extrusion_multiplier = 0.8
            for line in raft.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index],
                                                                       config.raftLayerThickness,
                                                                       config.raftSpeed, 0)
                        gcode_output.write(instruction)
                        self.previousPos = line[point_index]
            self.wait_point = raft.sub_lines[0][0]
            gcode_output.write(gcodeEnvironment.goToNextPoint(self.wait_point, True))
            gcode_output.write(gcodeEnvironment.wait_for_cooling(196, 60000))

            self.skip_retraction = False

        # @profile
        def switch_leaf(leaf):
            switch = {
                "skin": print_skin,
                "infill": print_infill,
                "hole": print_hole,
                "inner_boundary" : print_inner_shell,
                "inner_hole": print_inner_shell,
                "boundary": print_boundary,
                "skirt" : print_skirt,
                "support" : print_support,
                "raft" : print_raft,
                "top_raft" : print_top_raft
            }
            switch[leaf.type](leaf)

        # @profile
        def swith_node(node):
            switch = {
                "outline": print_node,
                "layer": print_layer,
                "island": print_node,
                "raft_layer": print_raft_layer,
                "contact_layer" : print_contact_layer

            }
            switch[node.type](node)

        def print_raft_layer(node):
            config.extrusion_multiplier = 1.1
            gcodeEnvironment.Z += config.raftLayerThickness
            for node in node.sub_lines:
                gotroughgroup(node)

            config.reset()

        def print_contact_layer(node):
            config.infillSpeed = 1100
            config.skinSpeed = 1000
            config.boundarySpeed = 1000
            config.holeSpeed = 1000
            config.exteriorFanSpeed = 1
            config.interiorFanSpeed = 1
            config.extrusion_multiplier = 1.2

            gcodeEnvironment.Z += config.layerThickness + 0.2

            for node in node.sub_lines:
                gotroughgroup(node)

            # gcode_output.write("M104 S220 \n")
            gcode_output.write(gcodeEnvironment.goToNextPoint(self.wait_point, True))
            gcode_output.write(gcodeEnvironment.wait_for_cooling(config.temperature, 25000))

            config.reset()

        # @profile
        def print_layer(node):
            if self.layer_index < 2:
                config.infillSpeed  = 1500
                config.skinSpeed = 1500
                config.boundarySpeed = 1500
                config.holeSpeed = 1500
                config.supportSpeed = 1500

            # allow change of layerThickness for each layer
            if self.layerThickness_list: # open happen if it is adaptive slicing
                config.layerThickness = self.layerThickness_list[self.layer_index]
            else:
                pass

            if self.layerThickness_list: # open happen if it is adaptive slicing
                gcodeEnvironment.Z += self.layerThickness_list[self.layer_index]
            else:
                gcodeEnvironment.Z += config.layerThickness

            for node in node.sub_lines:
                gotroughgroup(node)

            config.reset()

        # @profile
        def print_node(node):
            for node in node.sub_lines:
                gotroughgroup(node)

        # @profile
        def gotroughgroup(group):
            if (group.isLeaf):
                switch_leaf(group)
            else:
                swith_node(group)

        for layer_index in range(len(self.layer_list)):
            self.layer_index = layer_index
            if len(self.layer_list[layer_index].sub_lines) != 0:
                gotroughgroup(self.layer_list[layer_index])



        # gcode_output.write(gcodeEnvironment.retractFilament(config.retractionLength))
        gcode_output.write(gcodeEnvironment.endcode(printer_config.model))
        gcode_output.close()

        sys.stderr.write("GCode written")
