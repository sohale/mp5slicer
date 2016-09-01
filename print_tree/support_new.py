import slicer.config.config as config

from slicer.print_tree.Polygon_stack import Polygon_stack
from slicer.print_tree.Line_stack import Line_stack
from slicer.commons.utils import scale_list_to_clipper
from slicer.print_tree.infill_paterns import linear_infill2
import pyclipper
import datetime



def generate_support(polygon_layers, mesh_BBox):
    start_time = datetime.datetime.now()
    support_polylines_list = [[Line_stack(), Polygon_stack()] for i in range(len(polygon_layers))] # last layer has no support, so one less
    support_required_ps_list = [Polygon_stack() for i in range(len(polygon_layers))]

    if config.useSupport:
        innerlines_whole_bbox = Line_stack(scale_list_to_clipper(linear_infill2(config.supportSamplingDistance,config.support_line_angle,mesh_BBox)))
        support_required_ps = Polygon_stack(polygon_layers[-1])
        for layer_index in reversed(range(len(polygon_layers))):
            this_layer_index = layer_index
            one_below_layer_index = layer_index - 1
            if one_below_layer_index < 0:
                break

            # support required area calculation
            this_layer_outline = Polygon_stack(polygon_layers[this_layer_index])
            import math
            offset_value = config.layerThickness*math.tan(math.radians(config.supportOverhangangle))
            assert offset_value >= 0

            offseted_one_last_ps = Polygon_stack(polygon_layers[one_below_layer_index]).offset(offset_value)
            # offseted_one_last_ps = offseted_one_last_ps.remove_small_polygons(5)
            # old
            this_layer_support_required_ps = this_layer_outline.difference_with(offseted_one_last_ps)
            this_layer_support_required_ps = this_layer_support_required_ps.offset(config.support_area_enlarge_value) # think about the number

            support_required_ps = support_required_ps.difference_with(this_layer_outline)
            support_required_ps = support_required_ps.union_with(this_layer_support_required_ps)

            if config.does_remove_small_area:
                # clean small area
                support_required_ps = support_required_ps.remove_small_polygons(config.small_area)

            support_required_ps_list[one_below_layer_index] = support_required_ps

    # make one empty layer
    if config.one_empty_layer_between_support_and_model:
        for support_required_ps_index in range(len(support_required_ps_list)):
            if support_required_ps_index != len(support_required_ps_list) - 1:
                support_required_ps = support_required_ps_list[support_required_ps_index]
                one_top_ps = support_required_ps_list[support_required_ps_index + 1]

                last_layer_area = support_required_ps.difference_with(one_top_ps)
           
                support_required_ps = support_required_ps.difference_with(last_layer_area)
                support_required_ps_list[support_required_ps_index] = support_required_ps
    else:
        pass


    # generates lines from support required area
    for support_required_ps_index in range(len(support_required_ps_list)):
        support_required_ps = support_required_ps_list[support_required_ps_index]
        innerlines = innerlines_whole_bbox.intersect_with(support_required_ps)
        if support_required_ps_index in range(config.bed_support_strengthen_layer_number):
            offseted_line_polygon_stack = Polygon_stack()

            for i in reversed(range(config.bed_support_strengthen_offset_number)):
                offseted_line_polygon_stack.add_polygon_stack(innerlines.offset_line(config.line_width*(i+1)))

            support_polylines_list[support_required_ps_index] = [innerlines, offseted_line_polygon_stack]
        else:
            support_polylines_list[support_required_ps_index] = [innerlines, Polygon_stack()]

    # print(datetime.datetime.now() - start_time)

    return support_polylines_list