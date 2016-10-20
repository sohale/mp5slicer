from slicer.post_process.Tree_task import TreeTask
import slicer.config.config as config
from slicer.post_process.gcode_recorder import GcodeRecorder
from slicer.commons.utils import distance as calulate_distance
import numpy as np

class GcodeGenerator(TreeTask):
    def __init__(self, gcode_filename, layerthickness_list=[]):
        super().__init__()
        # self.gcodeEnvironment = GCodeEnvironment(gcode_filename)
        self.layer_index = 0
        self.layerthickness_list = layerthickness_list
        self.skip_retraction = False

        self.gcode_recorder = GcodeRecorder(gcode_filename)
        self.fan_speed = config.DEFAULT_FAN_SPEED
        self.speed = config.SPEED_RATE
        self.extrusion_multiplier = config.EXTRUSION_MULTIPLIER

        self.X = 0
        self.Y = 0  # this is only for calculDis
        self.Z = 0

    def __del__(self):
        self.gcode_recorder.write_gcode()

    def distance_to_self(self, A):
        return calulate_distance([self.X, self.Y], A)

    def type_gcode_start(self, type_str):
        self.gcode_recorder.append_type_start(type_str)

    def type_gcode_end(self, type_str):
        self.gcode_recorder.append_type_end(type_str)

    def append_rewrite_speed_fan_speed_extrusion_multiplier(
            self, speed, fan_speed, extrusion_multiplier):
        if self.speed != speed:
            self.gcode_recorder.append_rewrite_speed(speed)
            self.speed = speed
        else:
            pass
        if self.fan_speed != fan_speed:
            self.gcode_recorder.append_rewrite_fanspeed(fan_speed)
            self.fan_speed = fan_speed
        else:
            pass
        if self.extrusion_multiplier != extrusion_multiplier:
            self.gcode_recorder.append_change_extrusion_multiplier(extrusion_multiplier)
            self.extrusion_multiplier = extrusion_multiplier
        else:
            pass

    def basic_writing_gcode(
            self, line_group, speed, fan_speed, extrusion_multiplier):

        self.append_rewrite_speed_fan_speed_extrusion_multiplier(
            speed, fan_speed, extrusion_multiplier)
        for line in line_group.sub_lines:

            if len(line) > 0:
                dist = self.distance_to_self(line[0])
                if dist > config.MIN_RETRACTION_DISTANCE and \
                        not self.skip_retraction:
                    self.gcode_recorder.append_retract()
                    self.gcode_recorder.append_g0(line[0])
                    self.gcode_recorder.append_unretract()
                else:
                    self.gcode_recorder.append_g0(line[0])

                self.X, self.Y = line[0]

            for point_index in range(1, len(line)):
                if point_index == 1:
                    self.gcode_recorder.append_g1_change_speed(
                        line[point_index])
                else:
                    self.gcode_recorder.append_g1(line[point_index])
                self.X, self.Y = line[point_index]

        if self.skip_retraction:
            self.skip_retraction = False

    def writing_gcode_with_length_filter(
            self, line_group, speed, fan_speed,
            extrusion_multiplier, length_threshold):

        self.append_rewrite_speed_fan_speed_extrusion_multiplier(speed,
            fan_speed, extrusion_multiplier)
        for line in line_group.sub_lines:
            if len(line) > 0:
                dist = self.distance_to_self(line[0])

                if dist < length_threshold:
                    self.gcode_recorder.append_g1_change_speed(line[0])
                    self.X, self.Y = line[0]

                else:
                    distance = self.distance_to_self(line[0])
                    if distance > config.MIN_RETRACTION_DISTANCE and \
                            not self.skip_retraction:
                        self.gcode_recorder.append_retract()
                        self.gcode_recorder.append_g0(line[0])
                        self.gcode_recorder.append_unretract()
                        self.X, self.Y = line[0]

                    else:
                        self.gcode_recorder.append_g0(line[0])
                        self.X, self.Y = line[0]

                if self.skip_retraction:
                    self.skip_retraction = False

                for point_index in range(1, len(line)):

                    if point_index == 1:
                        self.gcode_recorder.append_g1_change_speed(
                            line[point_index])
                    else:
                        self.gcode_recorder.append_g1(line[point_index])

                    self.X, self.Y = line[point_index]

    def infill(self, line_group):
        self.type_gcode_start('infill')
        length_threshold = config.LINE_WIDTH * 2.5

        # self.skip_retraction = True
        self.writing_gcode_with_length_filter(
            line_group, config.INFILL_SPEED, config.INTERIOR_FAN_SPEED,
            config.EXTRUSION_MULTIPLIER, length_threshold)

        self.type_gcode_end('infill')

    def layer(self, line_group):
        if self.layer_index > 1:
            pass
        elif self.layer_index == 0:
            config.LINE_WIDTH = config.FIRST_LAYER_LINE_WIDTH
            config.INFILL_SPEED = config.FIRST_LAYER_INFILL_SPEED
            config.SKIN_SPEED = config.FIRST_LAYER_SKIN_SPEED
            config.BOUNDARY_SPEED = config.FIRST_LAYER_BOUNDARY_SPEED
            config.INNER_BOUNDARY_SPEED = config.FIRST_LAYER_INNER_BOUNDARY_SPEED
            config.HOLE_SPEED = config.FIRST_LAYER_HOLE_SPEED
            config.SUPPORT_SPEED = config.FIRST_LAYER_SUPPORT_SPEED
            config.RAFT_SPEED = config.FIRST_LAYER_RAFT_SPEED
            config.LAYER_THICKNESS = config.FIRST_LAYER_THICKNESS
            config.INTERIOR_FAN_SPEED = 0 # for sticking in the line

        elif self.layer_index == 1:
            config.reset()
        else:
            raise StandardError("layer_index doesn't make sense")

        # allow change of layerThickness for each layer
        if self.layerthickness_list:
            # open happen if it is adaptive slicing
            config.LAYER_THICKNESS = self.layerthickness_list[self.layer_index]
        else:
            pass

        self.type_gcode_start('layer')

        if self.layerthickness_list:
            # open happen if it is adaptive slicing
            z_change = self.layerthickness_list[self.layer_index]
        else:
            z_change = config.LAYER_THICKNESS

        import copy
        # only support 1 decimal place now
        assert z_change == 0 or len(str(z_change).split('.')[1]) in [1, 2]
        old_height = copy.copy(self.Z)
        self.Z += z_change
        self.Z = np.around(self.Z, decimals=2)
        # delete next line, for debug only
        if self.layer_index not in [0, 1]:
            assert np.around(self.Z - old_height, decimals=2) == \
                config.LAYER_THICKNESS
            pass

        self.gcode_recorder.append_change_z(self.Z)

        # self.gcode_recorder.append_unretract() # gcode_recorder
        speed = config.SPEED_RATE
        self.speed = config.SPEED_RATE
        self.gcode_recorder.append_rewrite_speed(speed)

        self.type_gcode_end('layer')
        self.layer_index += 1

    def raft_layer(self, line_group):
        config.EXTRUSION_MULTIPLIER = 1.1
        # self.gcodeEnvironment.Z += config.RAFT_LAYER_THICKNESS
        self.gcode_recorder.append_change_z(config.RAFT_LAYER_THICKNESS)
        config.reset()

    def contact_layer(self, line_group):
        config.INFILL_SPEED = 1100
        config.SKIN_SPEED = 1000
        config.BOUNDARY_SPEED = 1000
        config.HOLE_SPEED = 1000
        config.EXTERIOR_FAN_SPEED = 1
        config.INTERIOR_FAN_SPEED = 1
        config.EXTRUSION_MULTIPLIER = 1.2

        self.gcode_recorder.append_change_z(config.LAYER_THICKNESS + 0.2)

        config.reset()

    def skin(self, line_group):
        self.type_gcode_start('skin')
        length_threshold = config.LINE_WIDTH * 2.5
        # self.skip_retraction = True
        self.writing_gcode_with_length_filter(line_group,
                                              config.SKIN_SPEED,
                                              config.INTERIOR_FAN_SPEED,
                                              config.EXTRUSION_MULTIPLIER,
                                              length_threshold)
        self.type_gcode_end('skin')

    def hole(self, line_group):
        self.type_gcode_start('hole')
        self.basic_writing_gcode(line_group,
                                 config.HOLE_SPEED,
                                 config.EXTERIOR_FAN_SPEED,
                                 config.EXTRUSION_MULTIPLIER)
        self.type_gcode_end('hole')

    def inner_boundary(self, line_group):
        self.type_gcode_start('inner boundary')
        self.basic_writing_gcode(line_group,
                                 config.INNER_BOUNDARY_SPEED,
                                 config.DEFAULT_FAN_SPEED,
                                 config.EXTRUSION_MULTIPLIER)
        self.type_gcode_end('inner boundary')

    def inner_hole(self, line_group):
        self.type_gcode_start('inner_hole')
        self.basic_writing_gcode(line_group,
                                 config.BOUNDARY_SPEED,
                                 config.EXTERIOR_FAN_SPEED,
                                 config.EXTRUSION_MULTIPLIER)
        self.type_gcode_end('inner_hole')

    def boundary(self, line_group):
        self.type_gcode_start('boundary')
        self.basic_writing_gcode(line_group,
                                 config.BOUNDARY_SPEED,
                                 config.DEFAULT_FAN_SPEED,
                                 config.EXTRUSION_MULTIPLIER)
        self.type_gcode_end('boundary')

    def skirt(self, line_group):
        self.type_gcode_start('skirt')
        self.basic_writing_gcode(line_group,
                                 config.RAFT_SPEED,
                                 config.SKIRT_FAN_SPEED,
                                 config.EXTRUSION_MULTIPLIER)
        self.type_gcode_end('skirt')

    def support(self, line_group):
        self.type_gcode_start('support')
        length_threshold = config.LINE_WIDTH * 1.5
        # self.skip_retraction = True
        self.writing_gcode_with_length_filter(line_group,
                                              config.SUPPORT_SPEED,
                                              config.SUPPORT_FAN_SPEED,
                                              config.EXTRUSION_MULTIPLIER,
                                              length_threshold)
        self.type_gcode_end('support')

    def raft(self, line_group):
        self.type_gcode_start('raft')
        self.basic_writing_gcode(line_group,
                                 config.RAFT_SPEED,
                                 config.RAFT_FAN_SPEED,
                                 config.EXTRUSION_MULTIPLIER,
                                 config.RAFT_LAYER_THICKNESS)
        self.type_gcode_end('raft')

    def top_raft(self, line_group):
        self.type_gcode_start('top_raft')
        config.EXTRUSION_MULTIPLIER = 0.8
        self.basic_writing_gcode(line_group,
                                 config.RAFT_SPEED,
                                 config.RAFT_FAN_SPEED,
                                 config.EXTRUSION_MULTIPLIER,
                                 config.RAFT_LAYER_THICKNESS)
        self.wait_point = line_group.sub_lines[0][0]
        # self.gcode_output.write(self.gcodeEnvironment.goToNextPoint(self.wait_point, False))
        # self.gcode_output.write(self.gcodeEnvironment.wait_for_cooling(196, 60000))
        self.type_gcode_end('top_raft')
        config.reset()


'''
# these are the functions that is useful but not yet implemented
# because of the change of gcode writer

#     # a simple instrcuction that will retract filament
#     # call the caller: changeLayer (or nextLayer)
#     def retractFilament(self, retraction):
#         return "G1 F"+str(config.RETRACTION_SPEED) + " E" + \
#            str( max(0, (self.E - retraction) ) ) + "\n"


#     def volumeInLinear(self, A, B):
#         return (self.calculE(A,B)*config.crossArea) * config.volFactor

    # def wait_for_cooling(self, temp, time):
    #     instruction = self.retract()

    #     self.gcode_recorder.append_retract() # gcode_recorder

    #     self.fan_speed = 1
    #     if printer_config.model == "r2x":
    #         instruction += "M126 S" + str(self.fan_speed) + "\n"
    #     else:
    #         instruction += "M106 S" + str(int(np.floor(self.fan_speed * 255))) + "\n"
    #     instruction += "M104 S"+ str(temp) +" \n"
    #     instruction += "G4 P" + str(time) +" \n"
    #     instruction += self.unretract()

    #     self.gcode_recorder.append_unretract() # gcode_recorder

    #     return instruction
'''
