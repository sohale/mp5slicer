from gcode_writer import *
import pyclipper

import numpy as np

class Outline:
    def __init__(self,island,polygons):
        self.island = island
        self.polylines = self.make_polyline(polygons)


    def get_innershell(self,polygon):
        clipper_polygon = pyclipper.scale_to_clipper(polygon)
        po = pyclipper.PyclipperOffset()
        po.AddPaths(clipper_polygon,pyclipper.JT_SQUARE,pyclipper.ET_CLOSEDPOLYGON)
        return pyclipper.scale_from_clipper(po.Execute(pyclipper.scale_to_clipper(-0.3)))

    def get_polyline(self,polygon):
        polyline = []
        start_point = polygon[0] # frist vertex of the polygon
        start_point = Point2D(start_point[0],start_point[1])
        polyline.append(start_point)
        for point in polygon[1:]: # the rest of the vertices
            point = Point2D(point[0],point[1])
            polyline.append(point)
        # goes back to the start point since the polygon does not repeat the start (end) vertice twice
        polyline.append(start_point)
        return polyline

    def make_polyline(self,polygons):
        polylines = []
        for polygon in polygons:
            polyline = []
            polylines.append(self.get_polyline(polygon))
            innershell = self.get_innershell(polygon)
            polylines.append(self.get_polyline(innershell))
            innershell = self.get_innershell(innershell)
            polylines.append(self.get_polyline(innershell))
        return polylines

    def g_print(self):
        return self.polylines


class Infill:
    def __init__(self,island, layers,polygons,layer_index,dense,BBox):
        self.island = island
        self.dense = dense
        self.layers =layers
        self.BBox = BBox
        self.polyline = self.make_polyline(polygons, layer_index)


    def make_polyline(self,polygons,layer_index):

        # start of a layer
        if layer_index%2:
            horizontal_or_vertical = 'vertical'

        else:
            horizontal_or_vertical = 'horizontal'

        slice_min = np.min(self.BBox)
        slice_max = np.max(self.BBox)
        # first two layers and last two layers are set to be fully filled
        if layer_index == 1 or layer_index == 2 or layer_index == len(self.layers) - 1 or layer_index == len(self.layers) or self.dense:
            infill_line_segment = poly_layer_infill_line_segment(polygons, 0.3, horizontal_or_vertical, slice_min, slice_max)
        else: # low infill density
            infill_line_segment = poly_layer_infill_line_segment(polygons, 2, horizontal_or_vertical, slice_min, slice_max)


        for each_infill_lines in infill_line_segment:
            pass



    def g_prtint(self):
        return self.polyline

class Skin:
    def __init__(self,island,polyline):
        self.island = island
        self.polyline = polyline

    def g_prtint(self):
        return self.polyline

class Printed_line:
    def __init__(self,polyline):
        self.polyline = polyline

    def g_prtint(self):
        return self.polyline
