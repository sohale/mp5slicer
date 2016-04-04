from gcode_writer import *

class Outline:
    def __init__(self,polygons):
        self.polylines = self.make_polyline(polygons)

    def make_polyline(self,polygons):
        polylines = []
        for polygon in polygons:
            polyline = []
            polylines.append(polyline)
            start_point = polygon[0] # frist vertex of the polygon
            start_point = Point2D(start_point[0],start_point[1])
            polyline.append(start_point)
            for point in polygon[1:]: # the rest of the vertices
                point = Point2D(point[0],point[1])
                polyline(point)
            # goes back to the start point since the polygon does not repeat the start (end) vertice twice
            polyline.append(start_point)
        return polylines

    def g_prtint(self):
        return self.polyline


class Infill:
    def __init__(self,polyline):
        self.polyline = polyline

    def g_prtint(self):
        return self.polyline

class Skin:
    def __init__(self,polyline):
        self.polyline = polyline

    def g_prtint(self):
        return self.polyline

class Printed_line:
    def __init__(self,polyline):
        self.polyline = polyline

    def g_prtint(self):
        return self.polyline
