import math
import config
import printer_config

############################ GCodeEnvironment Taken from old slicer without any changes ###########################

class GCodeEnvironment:





    def __init__(self):

        self.settings = config


        self.E = 0
        self.F = 1000 # in mm/minute
        self.fan_speed = 0

        self.X = 0
        self.Y = 0
        self.Z = config.firstLayerOffset + config.layerThickness

    def truncate(self,f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        s = '{}'.format(f)
        if 'e' in s or 'E' in s:
            return float('{0:.{1}f}'.format(f, n))
        i, p, d = s.partition('.')
        return float('.'.join((i, (d+'0'*n)[:n])))


    # Calculate the extrusion for a straight movement from A to B
    def calculE(self,A,B):
        distance = math.sqrt( (pow((A[0]-B[0]),2)) + pow((A[1]-B[1]),2))
        section_surface = self.settings.layerThickness * self.settings.line_width
        volume = section_surface * distance * 1.1
        filament_length = volume / self.settings.crossArea
        # filament_length = self.truncate(filament_length, 4)
        return filament_length

    def calculDis(self,A):

        distance = math.sqrt( (pow((self.X-A[0]),2)) + pow((self.Y-A[1]),2))
        return distance

    # go to point A without extruding filament
    def goToNextPoint(self,A, retract,):
        B = [0.1]*2
        for i in range(len(A)):
            B[i] = self.truncate(A[i],3)
        A = B
        distance = self.calculDis(A)
        if distance > config.min_retraction_distance and retract:
            instruction = self.retract()

            instruction +=  "G0" + " X"+str(A[0]) + " Y"+str(A[1]) + " Z"+str(self.Z) +" F"+str(self.settings.inAirSpeed)+"\n"
            instruction += self.unretract()
        else :
            instruction =  "G0" + " X"+str(A[0]) + " Y"+str(A[1]) + " Z"+str(self.Z) + " F"+str(self.settings.inAirSpeed)+"\n"



        self.X = A[0]
        self.Y = A[1]
        return instruction

    def retract(self):
        self.E -= 5
        instruction = "G1 E" + str(self.E)+ " F2400\n"
        return instruction

    def unretract(self):
        self.E += 5
        instruction = "G1 E" + str(self.E)+ " F2400\n"
        return instruction


    # draw to point A
    def drawToNextPoint(self, A, speed = 0, fan_speed = 0):
        if fan_speed != self.fan_speed:
            self.fan_speed = fan_speed
            if printer_config.model == "r2x":
                instruction = "M126 S" + str(fan_speed) + "\n"
            else:
                instruction = "M106 S" + str(int(math.floor(fan_speed*255))) + "\n"
        else:
            instruction = ""
        if isinstance(A,str):
            raise StandardError
        if speed == 0:
            self.F = self.settings.speedRate
        else:
            self.F = speed

        B = [0.1]*2
        for i in range(len(A)):
            B[i] = self.truncate(A[i],3)
        A = B
        currentPoint = [self.X,self.Y,self.Z]
        try:
            extrusion = self.calculE(currentPoint,A)
            self.E += extrusion
        except:
            raise StandardError
        instruction += "G1" + " X" +str(A[0]) + " Y" +str(A[1]) + " Z" +str(self.Z) + " E" +str(self.E) + " F" +str(self.F) + "\n"
        self.X = A[0]
        self.Y = A[1]
        return instruction

    # a simple instrcuction that will retract filament
    # call the caller: changeLayer (or nextLayer)
    def retractFilament(self, retraction):
        return "G1 F"+str(self.settings.retractionSpeed) + " E" + str( max(0, (self.E - retraction) ) ) + "\n"


    def volumeInLinear(self, A, B):
        return (self.calculE(A,B)*self.settings.crossArea) * self.settings.volFactor




    # returns the code written in the file startcode.gcode
    def startcode(self, printer):
        if printer == "r2x":
            start_code_name = "r2xstart"
            startString = "M104 S"+str(config.temperature)+" T1 (set extruder temperature)\n"
        else:
            start_code_name = "startcode"
            startString = "M109 S"+str(config.temperature)+"\n"


        startCode = open(start_code_name + ".gcode","r")
        for line in startCode:
            startString = startString + line
        startCode.close()
        return startString

    # returns the code written in the file endcode.gcode
    def endcode(self,printer = 'default'):
        if printer == "r2x":
            end_code_name = "r2xend"
        else:
            end_code_name = "endcode"

        endString = ""
        endCode = open(end_code_name + ".gcode","r")
        for line in endCode:
            endString = endString + line
        endCode.close()
        return endString


