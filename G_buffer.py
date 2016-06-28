from slicer.gcode_writer import *
import slicer.config as config
import sys
import slicer.printer_config as printer_config
import copy
from slicer.utils import copy_module

class G_buffer:
    layer_list = []



    def __init__(self,to_file, gcode_filename = "", layerThickness_list = []):
        self.to_file = to_file
        self.gcode_filename = gcode_filename
        self.skip_retraction = False
        self.config = copy_module(config)
        self.layer_index = 0
        self.previousPos = None
        self.layerIslands = None
        self.layerThickness_list = layerThickness_list 

    def add_layer(self,list):
        self.layer_list.append(list)



    def print_Gcode(self):
        gcodeEnvironment = GCodeEnvironment()
        # create the gcode_output
        if self.to_file:
            gcode_output = open(self.gcode_filename, "w+")
        else:
            gcode_output = sys.stdout

        instruction = gcodeEnvironment.startcode(printer_config.model)
        gcode_output.write(instruction)

        # @profile
        def print_boundary(boundary):
            for line in boundary.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],True))
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.layerThickness, self.config.boundarySpeed, self.config.exteriorFanSpeed)
                        gcode_output.write(instruction)

            self.skip_retraction = False

        # @profile
        def print_hole(boundary):
            for line in boundary.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.layerThickness, self.config.holeSpeed, self.config.exteriorFanSpeed)
                        gcode_output.write(instruction)
            self.skip_retraction = False

        # @profile
        def print_infill(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.layerThickness, self.config.infillSpeed, self.config.interiorFanSpeed)
                        gcode_output.write(instruction)

        # @profile
        def print_skin(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.layerThickness , self.config.skinSpeed, self.config.interiorFanSpeed)
                        gcode_output.write(instruction)

        def print_support(leaf):
            for line in leaf.sub_lines:
                if len(line) > 0:
                    if self.skip_retraction:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0],False))
                        self.skip_retraction = False
                    else:
                        gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1,len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.layerThickness, self.config.supportSpeed, self.config.supportFanSpeed)
                        gcode_output.write(instruction)
            self.skip_retraction = False

        def print_inner_shell(shell):
            for line in shell.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.layerThickness , self.config.shellSpeed, self.config.interiorFanSpeed)
                        gcode_output.write(instruction)
            self.skip_retraction = False

        def print_skirt(skirt):
            for line in skirt.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.layerThickness, self.config.raftSpeed, 0.2)
                        gcode_output.write(instruction)
                        self.previousPos = line[point_index]
            self.skip_retraction = False

        def print_raft(raft):
            for line in raft.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index], self.config.raftLayerThickness, self.config.raftSpeed, 0)
                        gcode_output.write(instruction)
                        self.previousPos = line[point_index]
            self.skip_retraction = False

        def print_top_raft(raft):
            for line in raft.sub_lines:
                if len(line) > 0:
                    gcode_output.write(gcodeEnvironment.goToNextPoint(line[0], True))
                    for point_index in range(1, len(line)):
                        instruction = gcodeEnvironment.drawToNextPoint(line[point_index],
                                                                       self.config.raftLayerThickness,
                                                                       self.config.raftSpeed, 0)
                        gcode_output.write(instruction)
                        self.previousPos = line[point_index]
            self.wait_point = raft.sub_lines[0][0]
            gcode_output.write(gcodeEnvironment.goToNextPoint(self.wait_point, True))
            gcode_output.write(gcodeEnvironment.wait_for_cooling(210, 60000))

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
            self.config.extrusion_multiplier = 0.8
            gcodeEnvironment.Z += self.config.raftLayerThickness
            for node in node.sub_lines:
                gotroughgroup(node)

            self.config = copy_module(config)

        def print_contact_layer(node):
            self.config.infillSpeed = 1200
            self.config.skinSpeed = 700
            self.config.boundarySpeed = 700
            self.config.holeSpeed = 1000
            self.config.shellSpeed = 700
            self.config.exteriorFanSpeed = 0.6
            self.config.interiorFanSpeed = 0.6
            self.config.extrusion_multiplier = 2

            gcodeEnvironment.Z += self.config.layerThickness

            for node in node.sub_lines:
                gotroughgroup(node)

            # gcode_output.write("M104 S220 \n")
            gcode_output.write(gcodeEnvironment.goToNextPoint(self.wait_point, True))
            gcode_output.write(gcodeEnvironment.wait_for_cooling(config.temperature, 25000))

            self.config = copy_module(config)

        # @profile
        def print_layer(node):
            if self.layer_index < 2:
                self.config.infillSpeed  = 1500
                self.config.skinSpeed = 1500
                self.config.boundarySpeed = 1500
                self.config.holeSpeed = 1500
                self.config.shellSpeed = 1500
                self.config.supportSpeed = 1500

            # allow change of layerThickness for each layer
            if self.layerThickness_list: # open happen if it is adaptive slicing
                self.config.layerThickness = self.layerThickness_list[self.layer_index]
            else:
                pass

            if self.layerThickness_list: # open happen if it is adaptive slicing
                gcodeEnvironment.Z += self.layerThickness_list[self.layer_index]
            else:
                gcodeEnvironment.Z += self.config.layerThickness

            for node in node.sub_lines:
                gotroughgroup(node)

            self.config = copy_module(config)

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
