'''
This the a new gocode writer, it's able to do multiple polygon in one layer with no hole.
Todo: slice polygon with hole
'''
import math
import matplotlib.pyplot as plt
import numpy as np
import clipper
import pipeline_test
import pyclipper

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
# The following will help you understand the infill codes.
'''
Title: Write a 2D slicer.
A 2D slicer receives a planar shape (for example a polygon on the 2D
plane) and generates the region of the shape using horizontal lines.

Write a program for convex or non-convex polygon in form of a set of 2D coordinates.  
The physical unit of numbers is in millimeters.

The input contains two numbers dy. The slice layers are at:
y=some_start_value_for_y+k*dy, where k is an integer (k can be negative). The output should 
describe the output in the form of: a list of
"slice"s, each slice is a y value followed by intersecting x values. 
Each slice is like:
[ [y1, [intersection_0, intersection_1, ... ] ] , [y2, ...], ...]

Example input (note the number of significant digits): The coordinates
are in Cartesian system.
{"dy": -0.3333333,  "polygon": [[-1, 1], [1, -1], [0,
0.3333333]]}

Output format (Approximately):
[ [y1, [intersection_0, intersection_1, ... ] ] , [y2, ...], ...]
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

def scaled_offset(polygon_vertices, offset_value):
    #this function works for offset_value could be 0.1*n or -0.1*n, n = 0 to 10
    scaleup_polygon_vertices = [[i[0]*10,i[1]*10] for i in polygon_vertices]
    pco = pyclipper.PyclipperOffset()
    pco.AddPath(scaleup_polygon_vertices, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    solution = pco.Execute(offset_value*10)

    if solution != []:# polygon too small, offset to empty
        scaledown_polygon_vertices = [[i[0]/10,i[1]/10] for i in solution[0]]
    else:
        return polygon_vertices

    return scaledown_polygon_vertices

def ray_trace_polygon(polygon, dy, horizontal_or_vertical, slice_min, slice_max, boundary_or_hole, does_visualise=False):

    '''
    ray_trace a convex or non-convex polygon,
    output a list of intersecting point from a ray(could be horizontal or vertical)
    the following outputs are on horizontal rays
    Output format : [ [y1, [intersect_x_0, intersect_x_1, ...] ] , [y2, ...], ...]
    '''

    if boundary_or_hole == 'boundary': # offsetting polygon to make it smaller for infill
        res = scaled_offset(polygon,-0.5) # make the polygon 0.5 unit smaller # careful polygon only take integer value
    elif boundary_or_hole == 'hole':
        res = scaled_offset(polygon,0.6) # make the polygon 0.6 unit larger # careful polygon only take integer value

    else: # there should not be another type of polygon
        raise NotImplementedError('parameter boundary_or_hole can only be \'boundary\' or \'hole\'')

    if res != []: # this is the case the polygon is too small and offset to none
        offset_polygon = res
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
    else: # there should not be another type of infill lines
        raise NotImplementedError('parameter horizontal_or_vertical can only be horizontal or vertical')

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
            # if slope is inf corresponding x value is just domain value 
            result_x_inf = x_range[:,1][in_range_is_inf_boolean] 
            
            # combine the result
            result_x = np.append(result_x_not_inf,result_x_inf,axis=0)
                                
        # formatting for output format
        result_x = [i[0] for i in result_x.tolist()]
        result_list = [y,[]]
        for intersection_point in result_x:
            result_list[1].append(intersection_point)
        result_for_json.append(result_list)
    
    ############# visulisation ##############
    if does_visualise:
        for each_slice in result_for_json:
            y = each_slice[0]
            for pair_x in each_slice[1:]:
                if horizontal_or_vertical == 'horizontal':
                    plt.plot(pair_x,[y for i in pair_x],'-')
                else:
                    plt.plot([y for i in pair_x],pair_x,'-')
        plt.show()
    ############# visulisation ##############

    return result_for_json


def poly_layer_infill_line_segment(poly_layer, dy, horizontal_or_vertical, slice_min, slice_max, does_visualise=False):
    def merge_result_by_first_argument(result_all):

        '''
        this function is for combining the individual ray trace result for each polygon

        this function returns result_format_acsending_y.

        result_format_acsending_y is a list of 
        "slice"s, each slice is a y value followed by multiple pairs of x
        values. Each slice is like:
        [y1, [start_x_0, end_x_0], [start_x_1, end_x_1], ... ]
        the interpretation of this slice is there are line segment 
        [(start_x_0, y1), (end_x_0, y1)], [(start_x_1, y1), (end_x_1, y1)] ...

        so result_format_acsending_y looks like
        [ [y1, [start_x, end_x], [start_x, end_x], ... ] , [y2, ...], ...]
        '''

        final_result = {}
        for i in result_all[0]: # initialise final_result
            if len(i)>1:
                final_result[i[0]] = i[1]
            else:
                final_result[i[0]] = []

        for result in result_all[1:]: # loop through the rest 
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

        if does_visualise:
            for each_slice in result_format_acsending_y:
                y = each_slice[0]
                for pair_x in each_slice[1:]:
                    if horizontal_or_vertical == 'horizontal':
                        plt.plot(pair_x,[y for i in pair_x],'-')
                    else:
                        plt.plot([y for i in pair_x],pair_x,'-')
            plt.show()

        return result_format_acsending_y

    ray_trace_for_whole_layer = []
    # poly_layer is in the format [polygon_0,polygon_1..]
    # for each item in poly_layer, for exmaple polygon_0, polygon_1,  
    # the first thing in item is the boundary of polygon, 
    # polygon_0 = [boundary_polygon, hole_polygon, hole_polygon...]
    for polygon in poly_layer:
        boundary_polygon = polygon[0] # polygon[0] is the boundary of the polygon
        if len(boundary_polygon) > 2: # a polygon with length 2 is ill defined
            ray_trace_for_whole_layer.append(ray_trace_polygon(boundary_polygon, dy, horizontal_or_vertical, slice_min, slice_max, 'boundary', does_visualise=False))
        for hole_polygon in polygon[1:]:
            ray_trace_for_whole_layer.append(ray_trace_polygon(hole_polygon, dy, horizontal_or_vertical, slice_min, slice_max, 'hole', does_visualise=False))

    merged_result = merge_result_by_first_argument(ray_trace_for_whole_layer)

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

def get_slice_min_max(polygon_list, horizontal_or_vertical):

    min_all_polygon = []
    max_all_polygon = []
    for polygon in polygon_list:
        boundary = polygon[0]
        
        if horizontal_or_vertical == 'vertical':
            values = [i[0] for i in boundary]
        elif horizontal_or_vertical == 'horizontal':
            values = [i[1] for i in boundary]
        else: # there should be anyother type of infill line
            raise NotImplementedError('parameter horizontal_or_vertical can only be horizontal or vertical')
        
        min_this_polygon = min(values)
        max_this_polygon = max(values)

        min_all_polygon.append(min_this_polygon)
        max_all_polygon.append(max_this_polygon)
            
    return min(min_all_polygon), max(max_all_polygon)

############################### function for writing gcode ###############################
def writeGCode(slice_layers, filename, wtf_hack_for_polylayers = False):
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

    ############################# gcode for layers ################################  
    polylayers = polygonize_layers(slice_layers)  

    if wtf_hack_for_polylayers:  # a hack to change polylayers to suit the following formal, the side effect is to make all polygon into a boundary polygo
        polylayers_new = []
        for layer in polylayers:
            polylayers_new.append([])
            for polygon in layer:
                polylayers_new[-1].append([polygon])
        polylayers = polylayers_new
    else: # make sure the polylayers is in the following format
        pass
    # todo : make a function to seperate the polygon into boundaries and holes
    '''
    polylayers describes all the polygon in one layer. 
    polylayers is in the following format, 
    polylayers = [
        [ # first layer
            [ # first polygon, in this list the first polygon is the boundary of this polygon, the rest are the holes in the polygon
                [], # boundary
                [], # first hole
                ... # holes
            ],
            [ # second polygon
            ],
            ... # other polygon
        ],
        [] # second layer,
        ... # other layers
    ]

    example:   
    [
        [ # first layer 
            [ # first polygon
                [ # boundary
                    [0+50,7*3+50],[5*3+50,7*3+50],[5*3+50,5*3+50],[7*3+50,5*3+50],[7*3+50,0+50],[2*3+50,0+50],[2*3+50,2*3+50],[0+50,2*3+50]
                ],
                [ # hole
                    [1*3+50,3*3+50],[1*3+50,6*3+50],[4*3+50,6*3+50],[4*3+50,5*3+50],[2*3+50,5*3+50],[2*3+50,3*3+50]
                ],
                [ # hole
                    [4*3+50,3*3+50],[3*3+50,3*3+50],[3*3+50,4*3+50],[4*3+50,4*3+50]
                ],
                [ # hole
                    [3*3+50,1*3+50],[3*3+50,2*3+50],[5*3+50,2*3+50],[5*3+50,4*3+50],[6*3+50,4*3+50],[6*3+50,1*3+50]
                ],
                [],... # holes
            ],
            [ # second polygon
                ...
            ]
        ],

        [ # seconds layer
        ],

        .., # other layers
    ]
    '''
    total_number_layers = len(polylayers)
    layer_counter = 1
    for each_polylayer in polylayers: # each_polylayer is a list of polygon in one layer

        ######### boundary #########
        for polygon_list in each_polylayer: # multiple polygon in one layer
            for polygon in polygon_list: # each polygon
                start_point = polygon[0] # frist vertex of the polygon
                start_point = Point2D(start_point[0],start_point[1])
                gcodeFile.write(gcodeEnvironment.goToNextPoint(start_point))
                for point in polygon[1:]: # the rest of the vertices
                    point = Point2D(point[0],point[1])
                    gcodeFile.write(gcodeEnvironment.drawToNextPoint(point))
                # goes back to the start point since the polygon does not repeat the start (end) vertice twice
                gcodeFile.write(gcodeEnvironment.drawToNextPoint(start_point))
        ######### boundary end #########

        ######### infill #############  

        # start of a layer
        if layer_counter%2:
            horizontal_or_vertical = 'vertical'
        else:
            horizontal_or_vertical = 'horizontal'

        slice_min, slice_max = get_slice_min_max(each_polylayer, horizontal_or_vertical)
        # first two layers and last two layers are set to be fully filled
        if layer_counter == 1 or layer_counter == 2 or layer_counter == total_number_layers - 1 or layer_counter == total_number_layers:
            infill_line_segment = poly_layer_infill_line_segment(each_polylayer, 0.3, horizontal_or_vertical, slice_min, slice_max)
        else: # low infill density
            infill_line_segment = poly_layer_infill_line_segment(each_polylayer, 2, horizontal_or_vertical, slice_min, slice_max)

        for each_infill_lines in infill_line_segment: 
            try: 
                each_infill_lines[1][0] # to avoid no infill line required for this layer
            except IndexError: # no infill required for line
                # print('no infill required for line')
                pass
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
                else:
                    raise NotImplementedError('parameter horizontal_or_vertical can only be \'horizontal\' or \'vertical\'')
        # ######### infill end #############  

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
    stl_mesh = mesh.Mesh.from_file('elephant.stl')
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
    writeGCode(slice_layers,'elephant.gcode', wtf_hack_for_polylayers=True)

    # visualise raytrace for a layer
    # each_polylayer = [
    #                         [ # first polygon
    #                             [ # boundary
    #                                 [-25,-25],[25,-25],[25,25],[-25,25]
    #                             ],
    #                         ],
    #                         [
    #                             [ # boundary
    #                                 [-50+100,-50],[50+100,-50],[50+100,50],[-50+100,50]
    #                             ],
    #                         ]
    #                     ]
    # polylist_slicer(each_polylayer, 1, 'horizontal', -100, +100, does_visualise=True)

