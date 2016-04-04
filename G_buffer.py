from gcode_writer import *

class G_buffer:
    points = []
    filename= "tppt.gc"
    def __init__(self):
        pass

    def add_point_list(self,list):
        self.points.append(list)


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

        ///print layes

        gcodeFile.write(gcodeEnvironment.retractFilament(printSettings.retractionLength))
        gcodeFile.write(gcodeEnvironment.endcode())
        gcodeFile.close()

        print("GCode written")