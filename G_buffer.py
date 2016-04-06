from gcode_writer import *

class G_buffer:
    layer_list = []
    filename= "tppt.gcode"
    def __init__(self):
        pass

    def add_layer(self,list):
        self.layer_list.append(list)


    def print_Gcode(self):
        printSettings = PrintSettings({})
        gcodeEnvironment = GCodeEnvironment(printSettings)
        # create the gcodefile
        gcodeFile = open(self.filename, "w+")
        gcodeFile.write("M109 S"+str(printSettings.temperature)+"\n")
        gcodeFile.write(gcodeEnvironment.startcode())

        # print two lines to extrude filament
        gcodeFile.write(gcodeEnvironment.goToNextPoint(Point2D(0,0)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint(Point2D(180,0)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint(Point2D(180,5)))
        gcodeFile.write(gcodeEnvironment.drawToNextPoint(Point2D(0,5)))

        for layer in self.layer_list:
            if layer != None:
                for line in layer:
                    if len(line) > 0:
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line[0]))
                        for point_index in range(1,len(line)):
                            gcodeFile.write(gcodeEnvironment.drawToNextPoint(line[point_index]))
                gcodeEnvironment.Z += printSettings.layerThickness


        gcodeFile.write(gcodeEnvironment.retractFilament(printSettings.retractionLength))
        gcodeFile.write(gcodeEnvironment.endcode())
        gcodeFile.close()

        print("GCode written")