from slicer.post_process.Tree_task import Tree_task
import slicer.config.config as config
import slicer.config.printer_config as printer_config
import math
import sys

class Gcode_writer(Tree_task):

    def __init__(self, gcode_filename = "test.gcode", layerThickness_list = []):
        self.to_file = config.toFile
        self.gcode_filename = gcode_filename
        self.gcodeEnvironment = GCodeEnvironment()
        self.layer_index = 0
        self.previousPos = None
        self.layerThickness_list = layerThickness_list
        self.skip_retraction = False
        # create the gcode_output
        if self.to_file:
            self.gcode_output = open(self.gcode_filename, "w")
            instruction = ""
            for attr in dir(config):
                if not attr.startswith('__'):
                    instruction += ";" +str(attr)+ " : "+str(getattr(config, attr)) +" \n"
            self.gcode_output.write(instruction)

        else:
            self.gcode_output = sys.stdout

        ## gcode writing starts 
        instruction = self.gcodeEnvironment.startcode(printer_config.model)
        instruction += "G1 F200 E" + str(config.initial_extrusion) + "\n"
        self.gcode_output.write(instruction)

    def __del__(self):
        self.gcode_output.write(self.gcodeEnvironment.endcode(printer_config.model))
        self.gcode_output.close()

    def basic_writing_gcode(self, line_group, speed, fan_speed, layerThickness = None):
        if layerThickness == None:
            layerThickness = config.layerThickness

        line_count = 0
        for line in line_group.sub_lines:
            if len(line) > 0:
                self.gcode_output.write(self.gcodeEnvironment.goToNextPoint(line[0], self.skip_retraction))
                for point_index in range(1, len(line)):
                    instruction = self.gcodeEnvironment.drawToNextPoint(line[point_index], layerThickness, speed, fan_speed)
                    self.gcode_output.write(instruction)
        self.skip_retraction = False

    def type_gcode_start(self, type_str):
        self.gcode_output.write(self.gcodeEnvironment.type_gcode_start(type_str))

    def type_gcode_end(self, type_str):
        self.gcode_output.write(self.gcodeEnvironment.type_gcode_end(type_str))

    def writing_gcode_with_length_filter(self, line_group, layerThickness, speed, fan_speed, length_threshold):

        for line in line_group.sub_lines:
            if len(line) > 0:
                dist = self.gcodeEnvironment.calculDis(line[0])
                if dist < length_threshold:
                    instruction = self.gcodeEnvironment.drawToNextPoint(line[0], layerThickness, speed, fan_speed)
                    self.gcode_output.write(instruction)
                else:
                    self.gcode_output.write(self.gcodeEnvironment.goToNextPoint(line[0], self.skip_retraction))
                if self.skip_retraction:
                    self.skip_retraction = False

                for point_index in range(1,len(line)):
                    instruction = self.gcodeEnvironment.drawToNextPoint(line[point_index], layerThickness, speed, fan_speed)
                    self.gcode_output.write(instruction)

    def infill(self,line_group): # done
        self.gcodeEnvironment.type_gcode_start('infill')
        length_threshold = config.line_width * 2.5
        self.writing_gcode_with_length_filter(line_group, config.layerThickness, config.infillSpeed, config.interiorFanSpeed, length_threshold)
        self.gcodeEnvironment.type_gcode_end('infill')

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
        elif self.layer_index == 1:
            config.reset()
        else:
            raise StandardError

        # allow change of layerThickness for each layer
        if self.layerThickness_list: # open happen if it is adaptive slicing
            config.layerThickness = self.layerThickness_list[self.layer_index]
        else:
            pass

        if self.layerThickness_list: # open happen if it is adaptive slicing
            self.gcodeEnvironment.Z += self.layerThickness_list[self.layer_index]
        else:
            self.gcodeEnvironment.Z += config.layerThickness

        self.layer_index += 1

        self.type_gcode_start('layer')
        instruction = self.gcodeEnvironment.retract()
        instruction += "G0 Z{} F{}\n".format(self.gcodeEnvironment.Z,
                                        config.z_movement_speed)
        instrcuction = self.gcodeEnvironment.unretract()
        self.gcode_output.write(instruction)
        self.type_gcode_end('layer')

    def raft_layer(self, line_group): # done
        config.extrusion_multiplier = 1.1
        self.gcodeEnvironment.Z += config.raftLayerThickness
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

        self.gcodeEnvironment.Z += config.layerThickness + 0.2

        # self.gcode_output.write("M104 S220 \n")
        self.gcode_output.write(self.gcodeEnvironment.goToNextPoint(self.wait_point, False))
        self.gcode_output.write(self.gcodeEnvironment.wait_for_cooling(config.temperature, 25000))

        config.reset()

    def skin(self, line_group): # done
        self.type_gcode_start('skin')
        length_threshold = config.line_width * 2.5
        self.writing_gcode_with_length_filter(line_group, config.layerThickness, config.skinSpeed, config.interiorFanSpeed, length_threshold)
        self.type_gcode_end('hole')

    def hole(self, line_group): # done
        self.type_gcode_start('hole')
        self.basic_writing_gcode(line_group, config.holeSpeed, config.exteriorFanSpeed)
        self.type_gcode_end('hole')
    def inner_boundary(self, line_group): # done
        self.type_gcode_start('infill')
        self.basic_writing_gcode(line_group, config.boundarySpeed, config.default_fan_speed)
        self.type_gcode_end('infill')
    def inner_hole(self, line_group): # done
        self.type_gcode_start('inner_hole')
        self.basic_writing_gcode(line_group, config.boundarySpeed, config.exteriorFanSpeed)
        self.type_gcode_end('inner_hole')
    def boundary(self, line_group): # done
        self.type_gcode_start('boundary')
        self.basic_writing_gcode(line_group, config.boundarySpeed, config.default_fan_speed)
        self.type_gcode_end('boundary')
    def skirt(self, line_group): #done
        self.type_gcode_start('skirt')
        self.basic_writing_gcode(line_group, config.raftSpeed, config.skirtFanSpeed)
        self.type_gcode_end('skirt')
    def support(self, line_group): # done
        self.type_gcode_start('support')
        self.basic_writing_gcode(line_group, config.supportSpeed,config.supportFanSpeed)
        self.type_gcode_end('support')
    def raft(self, line_group): # done
        self.type_gcode_start('raft')
        self.basic_writing_gcode(line_group, config.raftSpeed, config.raftFanSpeed, config.raftLayerThickness)
        self.type_gcode_end('raft')
    def top_raft(self, line_group): # done
        self.type_gcode_start('top_raft')
        config.extrusion_multiplier = 0.8
        self.basic_writing_gcode(line_group, config.raftSpeed, config.raftFanSpeed, config.raftLayerThickness)
        self.wait_point = line_group.sub_lines[0][0]
        self.gcode_output.write(self.gcodeEnvironment.goToNextPoint(self.wait_point, False))
        self.gcode_output.write(self.gcodeEnvironment.wait_for_cooling(196, 60000))
        self.type_gcode_end('top_raft')  
        config.reset()

class GCodeEnvironment:

    def __init__(self):

        self.E = 0
        self.fan_speed = config.default_fan_speed
        self.speed = config.speedRate
        self.X = 0
        self.Y = 0
        self.Z = config.firstLayerOffset
        self.rewrite_speed = True

    @staticmethod
    def truncate(f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''

        s = '{}'.format(f)
        # if 'e' in s or 'E' in s: # in our case the float is not that large for the use of e
        #     return float('{0:.{1}f}'.format(f, n))
        i, p, d = s.partition('.')
        return float('.'.join((i, (d+'0'*n)[:n])))

    @staticmethod
    def truncate_return_str(f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''

        s = '{}'.format(f)
        # if 'e' in s or 'E' in s: # in our case the float is not that large for the use of e
        #     return float('{0:.{1}f}'.format(f, n))
        i, p, d = s.partition('.')
        return '.'.join((i, (d+'0'*n)[:n]))

    def calculDis(self,A):

        distance = math.sqrt( (pow((self.X-A[0]),2)) + pow((self.Y-A[1]),2))
        return distance

    def calculE(self, A, B, layerThickness):
        distance = math.sqrt( (pow((A[0]-B[0]),2)) + pow((A[1]-B[1]),2))
        section_surface = layerThickness * config.nozzle_size # layerThickness is possible to change for each layer
        volume = section_surface * distance * config.extrusion_multiplier
        filament_length = volume / config.crossArea
        return filament_length

    # go to point A without extruding filament
    # @profile
    def goToNextPoint(self, A, skip_retract):
        A = list(map(self.truncate, A, [3]*len(A)))
        distance = self.calculDis(A)
        if distance > config.min_retraction_distance and not skip_retract:
            instruction = self.retract()

            instruction +=  "G0" + " X"+str(A[0]) + " Y"+str(A[1]) + " F"+str(config.inAirSpeed)+"\n"
            instruction += self.unretract()
        else :
            instruction =  "G0" + " X"+str(A[0]) + " Y"+str(A[1]) + " F"+str(config.inAirSpeed)+"\n"



        self.X = A[0]
        self.Y = A[1]

        self.rewrite_speed = True
        return instruction

    def retract(self):
        self.E -= 5
        instruction = "G1 E" + self.truncate_return_str(self.E, 5)+ " F2400\n"

        return instruction

    def unretract(self):

        if self.E < 1900: # https://github.com/Ultimaker/CuraEngine/issues/14
            self.E += 5
            instruction = "G1 E" + str(self.truncate(self.E, 5))+ " F2400\n"
        else:
            instruction = "G92 E0\n"
            self.E = 0.0000
            instruction += "G1 E" + str(self.truncate(self.E, 5))+ " F2400\n"

        return instruction
    # draw to point A
    # @profile
    def drawToNextPoint(self, A, layerThickness, speed, fan_speed):
        if fan_speed != self.fan_speed:
            self.fan_speed = fan_speed
            if printer_config.model == "r2x":
                instruction = "M126 S" + str(fan_speed) + "\n"
            else:
                instruction = "M106 S" + str(int(math.floor(fan_speed*255))) + "\n"
        else:
            instruction = ""

        # instruction = ""
        # if isinstance(A,str):
        #     raise RuntimeError
        # A = B
        A = list(map(self.truncate, A, [3]*len(A)))
        currentPoint = [self.X,self.Y]
        if currentPoint == A:
            instruction = ""
            return instruction
        # try:
        extrusion = self.calculE(currentPoint, A, layerThickness)
        self.E += extrusion
        # except:
        #     raise RuntimeError
        if self.rewrite_speed or speed != self.speed:
            self.speed = speed
            self.rewrite_speed = False
            instruction += "G1" + " X" +str(A[0]) + " Y" +str(A[1]) + " E" + self.truncate_return_str(self.E, 5) + " F" +str(self.speed) + "\n"
        else:
            instruction += "G1" + " X" +str(A[0]) + " Y" +str(A[1]) + " E" + self.truncate_return_str(self.E, 5) + "\n"

        self.X = A[0]
        self.Y = A[1]
        return instruction

    # a simple instrcuction that will retract filament
    # call the caller: changeLayer (or nextLayer)
    def retractFilament(self, retraction):
        return "G1 F"+str(config.retractionSpeed) + " E" + str( max(0, (self.E - retraction) ) ) + "\n"


    def volumeInLinear(self, A, B):
        return (self.calculE(A,B)*config.crossArea) * config.volFactor

    def wait_for_cooling(self, temp, time):
        instruction = self.retract()
        self.fan_speed = 1
        if printer_config.model == "r2x":
            instruction += "M126 S" + str(self.fan_speed) + "\n"
        else:
            instruction += "M106 S" + str(int(math.floor(self.fan_speed * 255))) + "\n"
        instruction += "M104 S"+ str(temp) +" \n"
        instruction += "G4 P" + str(time) +" \n"
        instruction += self.unretract()
        return instruction




    # returns the code written in the file startcode.gcode
    def startcode(self, printer):
        if printer == "r2x":
            start_code_name = "gcode_writer/r2xstart"
            startString = "M104 S"+str(confistag.temperature)+" T1 (set extruder temperature)\n"
        else:
            start_code_name = "gcode_writer/startcode"
            startString = "M109 S"+str(config.temperature)+"\n"


        startCode = open(start_code_name + ".gcode","r")
        for line in startCode:
            startString = startString + line
        startCode.close()
        return startString

    # returns the code written in the file endcode.gcode
    def endcode(self,printer = 'default'):
        if printer == "r2x":
            end_code_name = "gcode_writer/r2xend"
        else:
            end_code_name = "gcode_writer/endcode"

        endString = ""
        endCode = open(end_code_name + ".gcode","r")
        for line in endCode:
            endString = endString + line
        endCode.close()
        return endString

    def type_gcode_start(self, type_str):
        return  "; {} starts \n".format(type_str)

    def type_gcode_end(self, type_str):
        return "; {} ends \n".format(type_str)



