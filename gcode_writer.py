'''
This the a new gocode writer, it's able to do multiple polygon in one layer with no hole.
Todo: slice polygon with hole
'''
import math
import matplotlib.pyplot as plt
import numpy as np
import clipper

slowDownTime = 0.03
slowDownFactor = 1

class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

############################ PrintSettings Taken from old slicer without any changes ###########################
class PrintSettings:
    #IT is immutable and does not have a self that updates itself.
    def __init__(self, argDictionnary):
        dic = PrintSettings.addDefaults(argDictionnary)
        for key,value in dic.items():
            setattr(self, key, value)
        #self.crossArea = 6.376 # cross-section area of feedstock
        self.crossArea = ((self.filamentDiameter/2.0)**2) * math.pi #6.37939
        print("cross area = "+str(self.crossArea))
        #specific to PLA:
        self.volFactor = 1/2.53 # vol of filament -> vol of extruded material


    #def getVolFactor():
    #    pass
    #def getArea():
    #    pass
    #pass
    @staticmethod
    def addDefaults(dict):
        try:
            dict["layerThickness"]
        except KeyError:
            dict["layerThickness"]=0.2
        try:
            dict["emptyLayer"]
        except KeyError:
            dict["emptyLayer"] = 0
        try:
            dict["infillSpace"]
        except KeyError:
            dict["infillSpace"]=4
        try:
            dict["topThickness"]
        except KeyError:
            dict["topThickness"]=0.6
        try:
            dict["paramSamples"]
        except KeyError:
            dict["paramSamples"]=75
        try:
            dict["name"]
        except KeyError:
            dict["name"]="test"
    #Speed in  mm/min
        try:
            dict["speedRate"]
        except KeyError:
            dict["speedRate"]=2000 # mm/min
        try:
            dict["circleSpeedRate"]
        except KeyError:
            dict["circleSpeedRate"]=1000
        try:
            dict["temperature"]
        except KeyError:
            dict["temperature"]=220
    #Speed in  mm/min
        try:
            dict["inAirSpeed"]
        except KeyError:
            dict["inAirSpeed"]=7000
        try:
            dict["flowRate"]
        except KeyError:
            dict["flowRate"] = 0.035  # mm/mm = mm (filament) /mm (nozzle)

        try:
            dict["criticalLength"]
        except KeyError:
            dict["criticalLength"]=35

        try:
            dict["retractionSpeed"]
        except KeyError:
            dict["retractionSpeed"]=2400

        try:
            dict["retractionLength"]
        except KeyError:
            dict["retractionLength"]=5
        #try:
        #    dict["areaFilament"]
        #except KeyError:
        #    dict["areaFilament"]=6.6
        try:
            dict["bottomLayerSpeed"]
        except KeyError:
            dict["bottomLayerSpeed"]=500

        try:
            dict["shellNumber"]
        except KeyError:
            dict["shellNumber"] = 3
        try:
            dict["critLayerTime"]
        except KeyError:
            dict["critLayerTime"] = 6
        # in seconds
        try:
            dict["zScarGap"]
        except KeyError:
            dict["zScarGap"] = 0.5
        try:
            dict["autoZScar"]
        except KeyError:
            dict["autoZScar"] = True
        try:
            dict["filamentDiameter"]
        except KeyError:
            dict["filamentDiameter"]=2.85

        #todo: filamentType = PLA or ABS

        saveEffectiveSettings = False
        if saveEffectiveSettings:
            #with fileLock:
            import json
            jsoncontent = json.dumps(dict)
            f1 = open("effectivesettings.json", "w+")
            f1.write(jsoncontent)

        return dict

############################ GCodeEnvironment Taken from old slicer without any changes ###########################

class GCodeEnvironment:

    #fixme: The following should be self.*, otherwise they are static.
    """
    E = 0
    F = 1000 # in mm/minute

    X = 0
    Y = 0
    Z = 0.3
    """
    shortLayer = False # tells if the layer is so short we need to wait before printing the next one
    nbLayers = 0
    layerTime = 0


    def __init__(self, printSettings):
        #print(self.Z," self.Z ",GCodeEnvironment.Z)
        self.settings = printSettings
        #print(self.Z," self.Z ",GCodeEnvironment.Z)

        self.E = 0
        self.F = 1000 # in mm/minute

        self.X = 0
        self.Y = 0
        self.Z = 0.3


    # Calculate the extrusion for a straight movement from A to B
    def calculE(self,A,B):
        distance = math.sqrt( (pow((A.x-B.x),2)) + pow((A.y-B.y),2))
        return (self.settings.flowRate*distance)

    def calculDis(self,A):
        #print(self)
        #print(A)
        distance = math.sqrt( (pow((self.X-A.x),2)) + pow((self.Y-A.y),2))
        return distance

    # go to point A without extruding filament
    def goToNextPoint(self,A):
        #if retractionSpeed == +Inf => dont
        currentPoint = Point3D(self.X,self.Y,self.Z)
        Ereduction = max(self.settings.retractionLength,self.calculE(currentPoint,A))
        instruction = "G1 F"+str(self.settings.retractionSpeed) + " E" + str( max(0, (self.E - Ereduction) ) ) + "\n"
        instruction = instruction + "G0" + " X"+str(A.x) + " Y"+str(A.y) + " Z"+str(self.Z) + " F"+str(self.settings.inAirSpeed)+"\n"
        # instruction = instruction + "airtime" + str(sqrt( (pow((self.X-A.x),2)) + pow((self.Y-A.y),2))/(self.settings.inAirSpeed/60)) + "\n"
        instruction = instruction +"G1" + " F" + str(self.settings.retractionSpeed) + " E" + str(self.E) + "\n"

        #fixme:precision. Maximum E.

        #update the current X,Y
        self.X = A.x
        self.Y = A.y
        return instruction

    def goToRestPoint(self,A):
        currentPoint = Point3D(self.X,self.Y,self.Z)
        Ereduction = max(self.settings.retractionLength,self.calculE(currentPoint,A))
        instruction = "G1 F"+str(self.settings.retractionSpeed) + " E" + str( max(0, (self.E - Ereduction) ) ) + "\n"
        instruction = instruction + "G0" + " X"+str(A.x) + " Y"+str(A.y) + " Z"+str(self.Z + 5) + " F"+str(self.settings.inAirSpeed)+"\n"
        instruction = instruction + "G0" + " X"+str(A.x) + " Y"+str(A.y) + " Z"+str(self.Z) + " F"+str(self.settings.inAirSpeed)+"\n"
        #instruction = instruction +"G1" + " F" + str(self.settings.retractionSpeed) + " E" + str(self.E) + "\n"
        #update the current X,Y
        self.X = A.x
        self.Y = A.y
        return instruction

    # draw to point A
    def drawToNextPoint(self,A):
        currentPoint = Point3D(self.X,self.Y,self.Z)
        self.E += self.calculE(currentPoint,A)
        Ereduction = max(self.settings.retractionLength,self.calculE(currentPoint,A))
        #self.F = self.getEffectiveVelocity(slowDownFactor,slowDownTime)
        if self.nbLayers==0:
            self.F=self.settings.bottomLayerSpeed
        elif self.layerTimeLinear(A) <= slowDownTime:
            self.F=self.settings.speedRate * slowDownFactor
        else:
            self.F=self.settings.speedRate
        instruction = "G1" + " X" +str(A.x) + " Y" +str(A.y) + " Z" +str(self.Z) + " E" +str(self.E) + " F" +str(self.F) + "\n"
        # instruction = instruction + "drawTime" + str(self.calculDis(A)/(self.F/60)) + "extusion time" + str(self.E/(2400/60)) +"\n"
        # instruction = instruction + "distancetime" + str(self.calculDis(A)) + "\n"
        #update the current X,Y
        self.X = A.x
        self.Y = A.y
        return instruction

    # a simple instrcuction that will retract filament
    # call the caller: changeLayer (or nextLayer)
    def retractFilament(self, retraction):
        return "G1 F"+str(self.settings.retractionSpeed) + " E" + str( max(0, (self.E - retraction) ) ) + "\n"

    def segmentLength(self, A, B):
        return sqrt( (pow((A.x-B.x),2)) + pow((A.y-B.y),2))

    def volumeInLinear(self, A, B):
        return (self.calculE(A,B)*self.settings.crossArea) * self.settings.volFactor

    def volumeInCircle(self, length):
        return (self.calculeCircleE(length)*self.settings.crossArea) * self.settings.volFactor

    def layerTimeLinear(self,A):
        return (self.calculDis(A)/(self.F/60))

    # pause the print by moving the nozzle away
    def pause(self,restPoint=Point2D(0,0),time=2000): #fixme: get time from selfsettings
        currentPoint = Point2D(self.X,self.Y)
        restPoint = currentPoint
        instruction = self.goToRestPoint(restPoint)
        #instruction = instruction +  "G4 P"+str(time)+"\n"
        # instruction = instruction + self.goToNextPoint(currentPoint)
        return instruction



    # returns the code written in the file startcode.gcode
    def startcode(self):
        startString = ""
        startCode = open("startcode.gcode","r")
        for line in startCode:
            startString = startString + line
        startCode.close()
        return startString

    # returns the code written in the file endcode.gcode
    def endcode(self):
        endString = ""
        endCode = open("endcode.gcode","r")
        for line in endCode:
            endString = endString + line
        endCode.close()
        return endString


############################ functions for infill ############################
# this is written by Tiger or the pre-assignment of intervel for myminifactory back in Dec/2015
# this infill code has not been optimised
# todo: a more generalised infill calculation, for example: allow hole in polygon
# The following will help you understand the infill.
'''
Title: Write a 2D slicer.
A 2D slicer receives a planar shape (for example a polygon on the 2D
plane) and generates the region of the shape using horizontal lines.

Write a program in Python that reads a Json file that describes a
convex or non-convex polygon in form of a set of 2D coordinates. The input file also
contains the angle of rotation of the polygonbefor being sliced. The
physical unit of numbers is in millimeters and the angle is in degrees
(rotation is around point [0,0]; we want to slice the the rotated object
only).

The input contains two numbers y0 and dy. The slice layers are at:
y=y0+k*dy, where k is an integer (k can be negative). The output should
be a Json file that describes the output in the form of: a list of
"slice"s, each slice is a y value followed by multiple pairs of x
values. Each slice is like:
[y1, [start_x, end_x], [start_x, end_x], ... ]

Note that if the start_x and end_x in a pair can be equal (i.e. the
intersection with a slice can be a single point). For example for the
following input, the output should be a json representation of a list
with five "slice" elements, each of them of the above format.

Example input (note the number of significant digits): The coordinates
are in Cartesian system.
{"dy": -0.3333333, "y0": 25, "polygon": [[-1, 1], [1, -1], [0,
0.3333333]],"angle":90}

Output format (Approximately):
[ [y1, [start_x, end_x], [start_x, end_x], ... ] , [y2, ...], ...]
'''

def between_y_value(row,number):
    if row[0] <= number <= row[1]:
        return True
    else:
        return False

def k2_minus_k1_not_zero(row):
    if row[1] - row[0] == 0:
        return False
    else:
        return True

def slope_is_inf(row):
    if np.isinf(row[0]):
        return True
    else:
        return False

def ray_trace_polygon(polygon, dy, horizontal_or_vertical, slice_min, slice_max, boundary_or_hole, does_visualise=False):

    '''
    ray_trace a convex or non-convex polygon,
    output a list of intersecting point from a ray(could be horizontal or vertical)
    the following outputs are on horizontal rays
    Output format : [ [y1, [intersect_x_0, intersect_x_1, ...] ] , [y2, ...], ...]
    '''

    polygon_for_clipper = [[]]# formatting for making polygon by clipper
    for i in polygon:
        polygon_for_clipper[0].append(clipper.Point(i[0],i[1]))

    if boundary_or_hole == 'boundary': # offsetting polygon to make it smaller for infill
        res = clipper.OffsetPolygons(polygon_for_clipper,-1) # make the polygon 1 unit smaller # careful polygon only take integer value
    elif boundary_or_hole == 'hole':
        res = clipper.OffsetPolygons(polygon_for_clipper,+1) # make the polygon 1 unit larger # careful polygon only take integer value
    else:
        raise NotImplementedError

    if res != []: # this is the case the polygon is too small and offset to none
        offset_polygon = list(zip([i.x for i in res[0]],[i.y for i in res[0]]))
    else:
        offset_polygon = polygon

    polygon_matrix = np.matrix(offset_polygon)
    rotated_polygon_matrix = np.roll(polygon_matrix, -1, axis=0)
    
    x_range = np.column_stack((polygon_matrix[:,0],
                        rotated_polygon_matrix[:,0]))
    y_range = np.column_stack((polygon_matrix[:,1],
                        rotated_polygon_matrix[:,1]))
    
    if horizontal_or_vertical == 'horizontal':
        pass
    elif horizontal_or_vertical == 'vertical': # a hack to calculate the vertical infill by flipping the x and y value
        x_range, y_range = y_range, x_range
        polygon_matrix = np.fliplr(polygon_matrix)
    # delete function when tangent = 0
    slope_not_zero_boolean = np.apply_along_axis(k2_minus_k1_not_zero, 1, y_range)
    x_range = x_range[slope_not_zero_boolean]
    y_range = y_range[slope_not_zero_boolean]
    
    # calculate slope k,intersection b
    k = (y_range[:,1] - y_range[:,0])/(x_range[:,1] - x_range[:,0])
    b = y_range[:,1] - np.multiply(k,x_range[:,1])
    
    # for later function range check
    y_range.sort(axis=1)

    # all slice y values
    y_value = np.arange(slice_min,
                        slice_max,
                        abs(dy))
    y_value = np.flipud(y_value) # reverse y_value

    result_for_json = []
    for y in y_value:
        
        in_range_boolean = np.apply_along_axis(between_y_value, 1, y_range, y)
        
        if not any(np.apply_along_axis(slope_is_inf, 1, k)): # no inf in k
            result_x = (y - b[in_range_boolean])/k[in_range_boolean]
        else:
            is_inf_boolean = np.apply_along_axis(slope_is_inf, 1, k)
            
            # deal with not inf slope
            in_range_not_inf_boolean = np.logical_and(np.logical_not(is_inf_boolean),
                                                      in_range_boolean)
            result_x_not_inf = (y - b[in_range_not_inf_boolean])/k[in_range_not_inf_boolean]
            
            # deal with inf slope
            in_range_is_inf_boolean = np.logical_and(is_inf_boolean,
                                                     in_range_boolean)
            # observed that if slope inf corresponding x value is just domain value 
            result_x_inf = x_range[:,1][in_range_is_inf_boolean] 
            
            # combine the result
            result_x = np.append(result_x_not_inf,result_x_inf,axis=0)
                                
        # formatting for output format
        result_x = [i[0] for i in result_x.tolist()]
        
        result_list = [y,[]]
        for i in result_x:
            result_list[1].append(i)
                        
        result_for_json.append(result_list)
        
    # if does_visualise:
    #     import matplotlib.pyplot as plt
    #     for each_slice in result_for_json:
    #         y = each_slice[0]
    #         for pair_x in each_slice[1:]:
    #             if horizontal_or_vertical == 'horizontal':
    #                 plt.plot(pair_x,[y for i in pair_x],'-')
    #             else:
    #                 plt.plot([y for i in pair_x],pair_x,'-')

    #     plt.show()

    return result_for_json

def polylist_slicer(data, dy, horizontal_or_vertical, slice_min, slice_max,does_visualise=False):
    def merge_result_by_first_argument(result_all):
        final_result = {}
        for i in result_all[0]:
            if len(i)>1:
                final_result[i[0]] = i[1]
            else:
                final_result[i[0]] = []

        for result in result_all[1:]:
            result = {i[0]:i[1] for i in result if len(i)>1}
            intersect_y = list(set(final_result.keys()) & set(result.keys()))
            difference_y = list(set(result.keys()) - set(final_result.keys()))

            for intersect in intersect_y:
                for i in result[intersect]:
                    final_result[intersect].append(i)
            for difference in difference_y:
                final_result[difference] = result[difference]

        result_format_acsending_y = []
        for key in sorted(final_result.keys()):

            result_x = sorted(final_result[key])
            result_x = [list(i) for i in zip(result_x[::2],result_x[1::2])]
            result_format_acsending_y.append(result_x)
            result_format_acsending_y[-1].insert(0, key)

        # if does_visualise:
        #     for each_slice in result_format_acsending_y:
        #         y = each_slice[0]
        #         for pair_x in each_slice[1:]:
        #             if horizontal_or_vertical == 'horizontal':
        #                 plt.plot(pair_x,[y for i in pair_x],'-')
        #             else:
        #                 plt.plot([y for i in pair_x],pair_x,'-')
        #     plt.show()

        return result_format_acsending_y

    # polygon_list is in the format [polygon_0,polygon_1..]
    # for each item in polygon_list, for exmaple polygon_0, polygon_1,  
    # the first thing in item is the boundary of polygon, 
    # polygon_0 = [boundary_polygon, hole_polygon, hole_polygon...]
    polygon_list = [
                                [
                                    [[0+50,7*3+50],[5*3+50,7*3+50],[5*3+50,5*3+50],[7*3+50,5*3+50],[7*3+50,0+50],[2*3+50,0+50],[2*3+50,2*3+50],[0+50,2*3+50]],
                                    [[1*3+50,3*3+50],[1*3+50,6*3+50],[4*3+50,6*3+50],[4*3+50,5*3+50],[2*3+50,5*3+50],[2*3+50,3*3+50]],
                                    [[4*3+50,3*3+50],[3*3+50,3*3+50],[3*3+50,4*3+50],[4*3+50,4*3+50]],
                                    [[3*3+50,1*3+50],[3*3+50,2*3+50],[5*3+50,2*3+50],[5*3+50,4*3+50],[6*3+50,4*3+50],[6*3+50,1*3+50]]
                                ]
                            ]

    result_all = []
    for polygon in polygon_list:
        result_all.append(ray_trace_polygon(polygon[0], dy, 'horizontal', slice_min, slice_max, 'boundary', does_visualise=False))
        
        for hole_polygon in polygon[1:]:
            result_all.append(ray_trace_polygon(hole_polygon, dy, 'horizontal', slice_min, slice_max, 'hole', does_visualise=False))
    merged_result = merge_result_by_first_argument(result_all)
    return merged_result
############################### function for slice_layers code taken from flavien's code on 30/MAR/16 ###############################
# this threshold for 0.00001 is change to 0.1 for 3d-printing purpose
def polygonize_layers(slice_layers):

    newslices = []
    for layer in slice_layers:
        newlayer = []
        for line in layer:
            line[0].pop()
            line[1].pop()
            newlayer.append(line)
        newslices.append(newlayer)

    slicesAsPolygons = []
    for slicee in newslices:
        polygons = []
        slicesAsPolygons.append(polygons)

        while True:
            try:
                line = slicee.pop()
            except IndexError:
                break

            start = line[0]
            end = line[1]

            newPolygon = []
            polygons.append(newPolygon)

            newPolygon.append(start)
            newPolygon.append(end)
            continuePolygon = True
            # Is there a new line i the polygon
            while continuePolygon:
                continuePolygon = False
                pointNotFound = True
                slicee2 = list(slicee)
                while pointNotFound:
                    try:
                        line2 = slicee2.pop()
                    except IndexError:
                        break
                    linePoint1 = line2[0]
                    linePoint2 = line2[1]
                    if (np.fabs(end[0] - linePoint2[0]) < 0.00001) and (np.fabs(end[1] - linePoint2[1]) < 0.00001):
                        if start != linePoint1:
                            # An other line in the polygon was found
                            slicee.remove(line2)
                            start = linePoint2
                            end = linePoint1
                            newPolygon.append(end)
                            continuePolygon = True
                            pointNotFound = False
                    if (np.fabs(end[0] - linePoint1[0]) < 0.00001) and (np.fabs(end[1] - linePoint1[1]) < 0.00001):
                        if start != linePoint2:
                            slicee.remove(line2)
                            start = linePoint1
                            end = linePoint2
                            newPolygon.append(end)
                            continuePolygon = True
                            pointNotFound = False

    return slicesAsPolygons

############################### function for writing gcode ###############################
def writeGCode(slice_layers, filename):
    printSettings = PrintSettings({})
    gcodeEnvironment = GCodeEnvironment(printSettings)
    # create the gcodefile
    gcodeFile = open(filename, "w+")
    gcodeFile.write("M109 S"+str(printSettings.temperature)+"\n")
    gcodeFile.write(gcodeEnvironment.startcode())

    # print two lines to extrude filament
    gcodeFile.write(gcodeEnvironment.goToNextPoint(Point2D(0,0)))
    gcodeFile.write(gcodeEnvironment.drawToNextPoint(Point2D(180,0)))
    gcodeFile.write(gcodeEnvironment.drawToNextPoint(Point2D(180,5)))
    gcodeFile.write(gcodeEnvironment.drawToNextPoint(Point2D(0,5)))

    #############################add stuff################################        
    polylayers = polygonize_layers(slice_layers)
    total_number_layers = len(polylayers)
    layer_counter = 1
    horizontal_or_vertical = 'horizontal'
    for point_list_layer in polylayers: # point_list_layer is a list of polygon in one layer
        # start of a layer
        if layer_counter%2:
            horizontal_or_vertical = 'vertical'
        else:
            horizontal_or_vertical = 'horizontal'

        ######### boundary #########
        for point_list in point_list_layer: # multiple polygon in one layer
            start_point = point_list[0]
            start_point = Point2D(start_point[0],start_point[1])
            gcodeFile.write(gcodeEnvironment.goToNextPoint(start_point))
            for point in point_list[1:]:
                point = Point2D(point[0],point[1])
                gcodeFile.write(gcodeEnvironment.drawToNextPoint(point))
            gcodeFile.write(gcodeEnvironment.drawToNextPoint(start_point)) # the printer ends at the start point
        ######### boundary end #########

        ######### infill #############  
        # first two layers and last two layers are set to be fully filled
        if layer_counter == 1 or layer_counter == 2 or layer_counter == total_number_layers - 1 or layer_counter == total_number_layers:
            infill_line_segment = polylist_slicer(point_list_layer, 0.3, horizontal_or_vertical, 0, 250)
        else: # low infill density
            infill_line_segment = polylist_slicer(point_list_layer, 2, horizontal_or_vertical, 0, 250)

        for each_infill_lines in infill_line_segment: 
            try: 
                each_infill_lines[1][0] # to avoid no infill line required for this layer
            except IndexError:
                print('no infill require this layer')
            else: # if there is no error occurs
                if horizontal_or_vertical == 'horizontal':
                    y = each_infill_lines[0]
                    segment_x_list = each_infill_lines[1:]
                    for x in segment_x_list:
                        line_segment_start = Point2D(x[0],y) 
                        line_segment_end = Point2D(x[1],y) 
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line_segment_start))
                        gcodeFile.write(gcodeEnvironment.drawToNextPoint(line_segment_end))
                elif horizontal_or_vertical == 'vertical':
                    x = each_infill_lines[0]
                    segment_y_list = each_infill_lines[1:] 
                    for y in segment_y_list:
                        line_segment_start = Point2D(x,y[0]) 
                        line_segment_end = Point2D(x,y[1]) 
                        gcodeFile.write(gcodeEnvironment.goToNextPoint(line_segment_start))
                        gcodeFile.write(gcodeEnvironment.drawToNextPoint(line_segment_end))

        ######### infill end #############  

        gcodeEnvironment.Z += printSettings.layerThickness
        layer_counter += 1

    gcodeFile.write(gcodeEnvironment.retractFilament(printSettings.retractionLength))
    gcodeFile.write(gcodeEnvironment.endcode())
    gcodeFile.close()

    print("GCode written")
    # todo: estimate that printing-time, printing-material

if __name__ == '__main__':
    from stl import mesh
    import slicer
    stl_mesh = mesh.Mesh.from_file('on_the_base.stl')
    # assume the center of the mesh are at (0,0)
    # translate x by 70 
    stl_mesh.vectors[:,:,0]+=70
    # translate y by 70
    stl_mesh.vectors[:,:,1]+=70
    slice_layers = slicer.slicer_from_mesh(stl_mesh, 
                            slice_height_from=0.3, 
                            slice_height_to=stl_mesh.max_[2], 
                            slice_step=0.3)

    # slicer.visualization_2d(slice_layers)
    writeGCode(slice_layers,'on_the_base.gcode')



    # polygon_list =  [[[0+50,7*3+50],[5*3+50,7*3+50],[5*3+50,5*3+50],[7*3+50,5*3+50],[7*3+50,0+50],[2*3+50,0+50],[2*3+50,2*3+50],[0+50,2*3+50]],
    #                             [[1*3+50,3*3+50],[1*3+50,6*3+50],[4*3+50,6*3+50],[4*3+50,5*3+50],[2*3+50,5*3+50],[2*3+50,3*3+50]],
    #                             [[4*3+50,3*3+50],[3*3+50,3*3+50],[3*3+50,4*3+50],[4*3+50,4*3+50]],
    #                             [[3*3+50,1*3+50],[3*3+50,2*3+50],[5*3+50,2*3+50],[5*3+50,4*3+50],[6*3+50,4*3+50],[6*3+50,1*3+50]]]
    # slice_layers = [[i,polygon_list] for i in range(10)]
    # writeGCode(slice_layers,'on_the_base.gcode')
    # res = polylist_slicer(data, 'vertical', slice_min=0,slice_max=14,does_visualise=True)

