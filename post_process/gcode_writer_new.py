from slicer.post_process.Tree_task import Tree_task
import slicer.config.config as config
import slicer.config.printer_config as printer_config
import sys
from slicer.post_process.gcode_recorder import Gcode_recorder
import numpy as np

class Gcode_writer(Tree_task):

    def __init__(self, gcode_filename, layerThickness_list = []):
        # self.gcodeEnvironment = GCodeEnvironment(gcode_filename)
        self.layer_index = 0
        self.layerThickness_list = layerThickness_list
        self.skip_retraction = False

        self.gcode_recorder = Gcode_recorder(gcode_filename)
        self.fan_speed = config.default_fan_speed
        self.speed = config.speedRate
        self.extrusion_multiplier = config.extrusion_multiplier

        self.X, self.Y = 0, 0 # this is only for calculDis

        self.Z = 0

    def __del__(self):        
        self.gcode_recorder.write_Gcode()

    def calculDis(self,A):
        distance = np.sqrt( (pow((self.X-A[0]),2)) + pow((self.Y-A[1]),2))
        return distance

    def type_gcode_start(self, type_str):
        self.gcode_recorder.append_type_start(type_str)

    def type_gcode_end(self, type_str):
        self.gcode_recorder.append_type_end(type_str)

    def append_rewrite_speed_fanspeed_extrusion_multiplier(self, speed, fan_speed, extrusion_multiplier):
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

    def basic_writing_gcode(self, line_group, speed, fan_speed, extrusion_multiplier):
        self.append_rewrite_speed_fanspeed_extrusion_multiplier(speed, fan_speed, extrusion_multiplier)
        for line in line_group.sub_lines:

            # self.gcode_recorder.append_rewrite_both_speed_and_extrusion_multiplier(speed, fan_speed, extrusion_multiplier)
            if len(line) > 0:
                dist = self.calculDis(line[0])
                if dist > config.min_retraction_distance and not self.skip_retraction:
                    self.gcode_recorder.append_retract()
                    self.gcode_recorder.append_g0(line[0]) # new
                    self.gcode_recorder.append_unretract()
                    # self.gcode_recorder.append_rewrite_speed(speed)
                else:
                    self.gcode_recorder.append_g0(line[0]) # new
                    # self.gcode_recorder.append_rewrite_speed(speed)

                self.X, self.Y = line[0]

                

            for point_index in range(1, len(line)):
                if point_index == 1:
                    self.gcode_recorder.append_g1_change_speed(line[point_index]) # new
                else:
                    self.gcode_recorder.append_g1(line[point_index]) # new
                self.X, self.Y = line[point_index]

        if self.skip_retraction:
            self.skip_retraction = False

    def writing_gcode_with_length_filter(self, line_group, speed, fan_speed, extrusion_multiplier, length_threshold):
        self.append_rewrite_speed_fanspeed_extrusion_multiplier(speed, fan_speed, extrusion_multiplier)
        for line in line_group.sub_lines:
            if len(line) > 0:
                dist = self.calculDis(line[0])
                
                if dist < length_threshold: 
                    # self.gcode_recorder.append_g1(line[0], speed)
                    self.gcode_recorder.append_g1_change_speed(line[0]) # new
                    self.X, self.Y = line[0]

                else:
                    distance = self.calculDis(line[0])
                    if distance > config.min_retraction_distance and not self.skip_retraction:
                        self.gcode_recorder.append_retract()
                        self.gcode_recorder.append_g0(line[0]) # new
                        self.gcode_recorder.append_unretract()
                        # self.gcode_recorder.append_rewrite_speed(speed)
                        self.X, self.Y = line[0]

                    else:
                        self.gcode_recorder.append_g0(line[0]) # new
                        # self.gcode_recorder.append_rewrite_speed(speed)
                        self.X, self.Y = line[0]


                if self.skip_retraction:
                    self.skip_retraction = False


                for point_index in range(1,len(line)):

                    if point_index == 1:
                        self.gcode_recorder.append_g1_change_speed(line[point_index]) # new
                    else:
                        self.gcode_recorder.append_g1(line[point_index])

                    self.X, self.Y = line[point_index]

    def infill(self,line_group): # done
        self.type_gcode_start('infill')
        length_threshold = config.line_width * 2.5

        # self.skip_retraction = True
        self.writing_gcode_with_length_filter(line_group, config.infillSpeed, config.interiorFanSpeed, config.extrusion_multiplier,  length_threshold)
        self.type_gcode_end('infill')

    def layer(self,line_group): # done
        if self.layer_index > 1:
            pass
        elif self.layer_index == 0:
            config.line_width = config.first_layer_line_width
            config.infillSpeed = config.first_layer_infillSpeed  
            config.skinSpeed = config.first_layer_skinSpeed
            config.boundarySpeed = config.first_layer_boundarySpeed
            config.holeSpeed = config.first_layer_holeSpeed
            config.shellSpeed = config.first_layer_shellSpeed
            config.supportSpeed = config.first_layer_supportSpeed
            config.raftSpeed = config.first_layer_raftSpeed
            config.layerThickness = config.first_layer_thickness
            config.interiorFanSpeed = 0 # for sticking in the line 

        elif self.layer_index == 1:
            config.reset()
        else:
            raise StandardError("layer_index doesn't make sense")

        # allow change of layerThickness for each layer
        if self.layerThickness_list: # open happen if it is adaptive slicing
            config.layerThickness = self.layerThickness_list[self.layer_index]
        else:
            pass

        self.type_gcode_start('layer')

        # self.gcode_recorder.append_retract() # gcode_recorder
        
        if self.layerThickness_list: # open happen if it is adaptive slicing
            z_change = self.layerThickness_list[self.layer_index]
        else:
            z_change = config.layerThickness

        import copy
        assert z_change == 0 or len(str(z_change).split('.')[1]) in [1, 2] # only support 1 decimal place now
        old_height = copy.copy(self.Z)
        self.Z += z_change
        self.Z = np.around(self.Z, decimals = 2)
        # delete next line, for debug only 
        if self.layer_index not in [0, 1]:
            assert np.around(self.Z - old_height, decimals = 2) == config.layerThickness
            pass

        self.gcode_recorder.append_change_z(self.Z)
   


        # self.gcode_recorder.append_unretract() # gcode_recorder
        speed = config.speedRate
        self.speed = config.speedRate
        self.gcode_recorder.append_rewrite_speed(speed)

        self.type_gcode_end('layer')
        self.layer_index += 1

    def raft_layer(self, line_group): # done
        config.extrusion_multiplier = 1.1
        # self.gcodeEnvironment.Z += config.raftLayerThickness
        self.gcode_recorder.append_change_z(config.raftLayerThickness)
        config.reset()

    def contact_layer(self, line_group): # done
        config.infillSpeed = 1100
        config.skinSpeed = 1000
        config.boundarySpeed = 1000
        config.holeSpeed = 1000
        config.shellSpeed = 1200
        config.exteriorFanSpeed = 1
        config.interiorFanSpeed = 1
        config.extrusion_multiplier = 1.2

        self.gcode_recorder.append_change_z(config.layerThickness + 0.2)

        # self.gcode_output.write("M104 S220 \n")
        # self.gcode_output.write(self.gcodeEnvironment.goToNextPoint(self.wait_point, False))
        # self.gcode_output.write(self.gcodeEnvironment.wait_for_cooling(config.temperature, 25000))

        config.reset()

    def skin(self, line_group): # done
        self.type_gcode_start('skin')
        length_threshold = config.line_width * 2.5
        # self.skip_retraction = True
        self.writing_gcode_with_length_filter(line_group, config.skinSpeed, config.interiorFanSpeed, config.extrusion_multiplier, length_threshold)
        self.type_gcode_end('skin')

    def hole(self, line_group): # done
        self.type_gcode_start('hole')
        self.basic_writing_gcode(line_group, config.holeSpeed, config.exteriorFanSpeed, config.extrusion_multiplier)
        self.type_gcode_end('hole')
    def inner_boundary(self, line_group): # done
        self.type_gcode_start('inner boundary')
        self.basic_writing_gcode(line_group, config.boundarySpeed, config.default_fan_speed, config.extrusion_multiplier)
        self.type_gcode_end('inner boundary')
    def inner_hole(self, line_group): # done
        self.type_gcode_start('inner_hole')
        self.basic_writing_gcode(line_group, config.boundarySpeed, config.exteriorFanSpeed, config.extrusion_multiplier)
        self.type_gcode_end('inner_hole')
    def boundary(self, line_group): # done
        self.type_gcode_start('boundary')
        self.basic_writing_gcode(line_group, config.boundarySpeed, config.default_fan_speed, config.extrusion_multiplier)
        self.type_gcode_end('boundary')
    def skirt(self, line_group): #done
        self.type_gcode_start('skirt')
        self.basic_writing_gcode(line_group, config.raftSpeed, config.skirtFanSpeed, config.extrusion_multiplier)
        self.type_gcode_end('skirt')
    def support(self, line_group): # done
        self.type_gcode_start('support')
        self.basic_writing_gcode(line_group, config.supportSpeed, config.supportFanSpeed, config.extrusion_multiplier)
        self.type_gcode_end('support')
    def raft(self, line_group): # done
        self.type_gcode_start('raft')
        self.basic_writing_gcode(line_group, config.raftSpeed, config.raftFanSpeed,config.extrusion_multiplier,  config.raftLayerThickness)
        self.type_gcode_end('raft')
    def top_raft(self, line_group): # done
        self.type_gcode_start('top_raft')
        config.extrusion_multiplier = 0.8
        self.basic_writing_gcode(line_group, config.raftSpeed, config.raftFanSpeed, config.extrusion_multiplier, config.raftLayerThickness)
        self.wait_point = line_group.sub_lines[0][0]
        # self.gcode_output.write(self.gcodeEnvironment.goToNextPoint(self.wait_point, False))
        # self.gcode_output.write(self.gcodeEnvironment.wait_for_cooling(196, 60000))
        self.type_gcode_end('top_raft')  
        config.reset()


'''
# these are the functions that is useful but not yet implemented because of the change of gcode writer

#     # a simple instrcuction that will retract filament
#     # call the caller: changeLayer (or nextLayer)
#     def retractFilament(self, retraction):
#         return "G1 F"+str(config.retractionSpeed) + " E" + str( max(0, (self.E - retraction) ) ) + "\n"


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



