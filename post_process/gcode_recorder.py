import slicer.config.config as config
import numpy as np
import slicer.config.printer_config as printer_config
from slicer.commons.utils import distance as calulate_distance
import sys


class G(object):
    '''Vectorised calculation for handling G0, G1 extrusion calculation'''
    def __init__(self):
        self.commands = []

    def append_g(self, x, y):
        self.commands.append([x, y])

    def calculE(self, extrusion_multiplier_list):
        commands = np.array(self.commands)[:, :2]
        layer_thickness = np.array([config.layerThickness for i in
                                   range(len(commands)-1)])

        # truncation
        commands = np.floor(commands*1000)/1000
        self.commands = commands
        commands_next_point = commands[1:]
        commands = commands[:-1]

        distance = np.linalg.norm(commands-commands_next_point, axis=1)
        # layer_thickness is possible to change for each layer
        section_surface = layer_thickness * config.nozzle_size
        volume = section_surface * distance * extrusion_multiplier_list
        filament_length = volume / config.crossArea
        self.E = filament_length.tolist()
        self.E.insert(0, 0)

    def calculE_test(self, extrusion_multiplier_list):
        '''this function is only for testing purposes'''
        def calculE_slow(point_0, point_1, layer_thickness):
            distance = calulate_distance(point_0, point_1)
            # layer_thickness is possible to change for each layer
            section_surface = layer_thickness * config.nozzle_size
            volume = section_surface * distance
            filament_length = volume / config.crossArea
            return filament_length

        res = []
        for i, j, k in zip(self.commands,
                           self.commands[1:],
                           extrusion_multiplier_list):
            res.append(calculE_slow(i, j, config.layer_thickness)*k)
        res = np.array(res)
        res = res.tolist()
        res.insert(0, 0)
        return res

    def get_extrusion_by_index(self, index):
        return self.E[index]

'''
Problems of gcode recorder, need to store lots of imformation in a list form,
this uses too much of memory?

And a specific index for commands 5,6,7,8, if this ever gets more, the code
will be messy.

'''
class GcodeRecorder:
    ''' 
    To save gcode into a list of commands and parameter for later
    translation into actual gcode
    '''
    def __init__(self, gcode_filename="test.gcode"):
        self.G = G()
        self.E = 0
        self.gcode_filename = gcode_filename

        if config.toFile:
            self.gcode_output = open(self.gcode_filename, "w")
        else:
            self.gcode_output = sys.stdout

        '''
        Commands is a place to tell printer what to do in progressive order.
        Commands is a list of value 0, 1, 2, 3, 4, 5, 6

        0 - write G0 with retraction
        1 - write G1
        2 - write retract
        3 - write unretract
        4 - write change z
        5 - rewrite speed signal
        6 - rewrite fan speed signal
        7 - comments type starts
        8 - comments type ends
        9 - change extrusion multiplier
        10 - write G1 with speed change
        '''
        self.commands = []

        self.Z = []
        self.z_index = 0
        self.current_layer_height = 0

        self.fan_speed = []
        self.fan_speed_function = self.prepare_change_fanspeed_function()
        self.fan_speed_index = 0
        self.current_fanspeed = 0

        self.speed = []
        self.speed_index = 0
        self.current_speed = 0

        self.type_start = []
        self.type_start_index = 0
        self.type_end = []
        self.type_end_index = 0

        self.extrusion_multiplier = []

        self.retract_string = "G92 E0\nG1 E-4.0000 F{}\n".format(config.retractionSpeed)
        self.unretract_string = "G1 E0.0000 F{}\nG92 E0\n".format(config.retractionSpeed)

        self.g0 = self.prepare_g0_function()
        self.change_z = self.prepare_change_z_function()
        # testing
        self.X, self.Y = 0, 0

    def reset_E(self):
        self.E = 0

    def make_extrusion_multiplier_array(self):
        extrusion_multiplier_index = 0
        extrusion_multiplier_list = []
        extrusion_multiplier = config.extrusion_multiplier
        for i in self.commands:
            if i == 0:
                extrusion_multiplier_list.append(0)
            elif i in [1, 10]:
                extrusion_multiplier_list.append(extrusion_multiplier)
            elif i == 9:
                extrusion_multiplier = self.extrusion_multiplier[extrusion_multiplier_index]
                extrusion_multiplier_index += 1

        # hack : first one is always G0, prepare for calculE
        extrusion_multiplier_list = extrusion_multiplier_list[1:]
        return np.array(extrusion_multiplier_list)

    ########### prepare function for specific printer ###########
    @staticmethod
    def prepare_change_fanspeed_function():
        if printer_config.model == "r2x":
            return lambda fan_speed: "M126 S{}\n".format(fan_speed)
        else:
            return lambda fan_speed: "M106 S{:d}\n".format(int(fan_speed*255))

    @staticmethod
    def prepare_g0_function():
        func = lambda x, y: "G0 X{:.3f} Y{:.3f} F{}\n".format(x,
                                                              y,
                                                              config.inAirSpeed)
        return func

    @staticmethod
    def prepare_change_z_function():
        func = lambda z: "G0 Z{:.3f} F{}\n".format(z, config.z_movement_speed)
        return func

    ########### function to append information into gcode recorder ###########
    def append_retract(self):
        self.commands.append(2)

    def append_unretract(self):
        self.commands.append(3)

    def append_g0(self, line):
        self.commands.append(0)
        self.G.append_g(line[0], line[1])

    def append_g1(self, line):
        self.commands.append(1)
        self.G.append_g(line[0], line[1])

    def append_g1_change_speed(self, line):
        self.commands.append(10)
        self.G.append_g(line[0], line[1])

    def append_change_z(self, z):
        self.commands.append(4)
        self.Z.append(z)

    def append_rewrite_speed(self, speed):
        self.commands.append(5)
        self.speed.append(speed)

    def append_rewrite_fanspeed(self, fan_speed):
        self.commands.append(6)
        self.fan_speed.append(fan_speed)

    def append_type_start(self, type_str):
        self.commands.append(7)
        self.type_start.append(type_str)

    def append_type_end(self, type_str):
        self.commands.append(8)
        self.type_end.append(type_str)

    def append_change_extrusion_multiplier(self, extrusion_multiplier):
        self.commands.append(9)
        self.extrusion_multiplier.append(extrusion_multiplier)

    ########### functions to get the gcode instruction ###########
    def get_change_z_gcode(self):
        instruction = self.change_z(self.Z[self.z_index])
        self.z_index += 1
        return instruction

    @property
    def startcode(self):

        if printer_config.model == "r2x":
            start_code_name = "gcode_writer/r2xstart"
            start_string = "M104 S{} T1 (set extruder temperature)\n".format(
                config.extruder_temperature)

        elif printer_config.model == "um2":
            start_code_name = "gcode_writer/um2_startcode"
            start_string = "M140 S{}\nM109 S{}\n".format(
                config.bed_temperature, 
                config.extruder_temperature)

        elif printer_config.model == "umo":
            start_code_name = "gcode_writer/startcode"
            start_string = "M109 S{}\n".format(config.extruder_temperature)
        else:
            raise NotImplementedError("only support r2x, um2, umo")

        start_code = open(start_code_name + ".gcode", "r")
        for line in start_code:
            start_string += line
        start_code.close()
        return start_string

    @property
    def endcode(self):
        if printer_config.model == "r2x":
            end_code_name = "gcode_writer/r2xend"
        elif printer_config.model == "um2":
            end_code_name = "gcode_writer/um2_endcode"
        elif printer_config.model == "umo":
            end_code_name = "gcode_writer/endcode"
        else:
            raise NotImplementedError("Supports for Printer models r2x, um2, umo")

        end_string = ""
        end_code = open(end_code_name + ".gcode", "r")
        for line in end_code:
            end_string += line
        end_code.close()
        return end_string

    # @staticmethod
    # def get_config():
    #     instruction = ""
    #     for attr in dir(config):
    #         if not attr.startswith('__'):
    #             instruction += ";" +str(attr)+ " : "+str(getattr(config, attr)) +" \n"
    #     return instruction

    def get_change_fanspeed_code(self):
        fan_speed = self.fan_speed[self.fan_speed_index]
        instruction = self.fan_speed_function(fan_speed)
        self.fan_speed_index += 1

        return instruction

    def get_type_gcode_start(self):
        type_str = self.type_start[self.type_start_index]
        self.type_start_index += 1
        return  "; {} starts \n".format(type_str)

    def get_type_gcode_end(self):
        type_str = self.type_end[self.type_end_index]
        self.type_end_index += 1
        return "; {} ends \n".format(type_str)

    def get_g0(self, x, y):
        return self.g0(x, y)

    @staticmethod
    def get_g1(x, y, E):
        return "G1 X{:.3f} Y{:.3f} E{:.5f}\n".format(x, y, E)

    @staticmethod
    def get_g1_with_speed_change(x, y, E, speed):
        # fun fact : this is faster then "G1 X{} Y{} E{} F{}\n".format(x, y, E, speed)
        return "G1 X{:.3f} Y{:.3f} E{:.5f} F{}\n".format(x, y, E, speed)

    # @staticmethod
    # def calculE(A, B, layer_thickness):
    #     distance = np.sqrt( (pow((A[0]-B[0]),2)) + pow((A[1]-B[1]),2))
    #     section_surface = layer_thickness * config.nozzle_size # layer_thickness is possible to change for each layer
    #     volume = section_surface * distance * config.extrusion_multiplier
    #     filament_length = volume / config.crossArea
    #     return filament_length

    def write_gcode(self):

        self.G.calculE(self.make_extrusion_multiplier_array())
        # code for testing E
        # res = self.G.calculE_test(self.make_extrusion_multiplier_array())
        # for i,j in zip(self.G.E, res):
        #     print(i,j)

        instruction = self.startcode
        instruction += "G1 F200 E{}\n".format(config.initial_extrusion)
        self.gcode_output.write(instruction)
        g_index = 0
        for commands_identifier in self.commands:

            if commands_identifier in [0, 1, 10]:
                self.E += self.G.get_extrusion_by_index(g_index)
                g_data = self.G.commands[g_index]
                g_index += 1

                if commands_identifier == 0: # write g0 with retraction
                    instruction = self.get_g0(g_data[0], g_data[1])
                elif commands_identifier == 1: # write g1
                    instruction = self.get_g1(g_data[0], g_data[1], self.E)
                else: # write g1 with speed change
                    instruction = self.get_g1_with_speed_change(g_data[0],
                                                                g_data[1],
                                                                self.E,
                                                                self.current_speed)
            elif commands_identifier == 2: # write retraction
                instruction = self.retract_string

            elif commands_identifier == 3: # write unretraction
                instruction = self.unretract_string
                self.reset_E()

            elif commands_identifier == 4: # write change z
                instruction = self.get_change_z_gcode()

            # notify change speed actual change speed is written in g1
            elif commands_identifier == 5:
                instruction = ""
                self.current_speed = self.speed[self.speed_index]
                self.speed_index += 1

            elif commands_identifier == 6: # write change fan speed
                instruction = self.get_change_fanspeed_code()

            elif commands_identifier == 7: # write change fan speed
                instruction = self.get_type_gcode_start()

            elif commands_identifier == 8: # write change fan speed
                instruction = self.get_type_gcode_end()

            elif commands_identifier == 9: # change extrusion multiplier
                instruction = ""

            else:
                raise NotImplementedError

            self.gcode_output.write(instruction)

        instruction = self.endcode
        self.gcode_output.write(instruction)
        self.gcode_output.close()
