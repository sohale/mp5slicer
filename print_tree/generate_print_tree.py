from slicer.print_tree.layer import Layer
from slicer.print_tree.raft_layer import Raft_layer
import slicer.config.config as config

def generate_tree(polygon_layers, BBox):

    layer_list = []
    for layer_index in range(len(polygon_layers)):
        layer = Layer(layer_list ,polygon_layers ,layer_index ,BBox)
        layer_list.append(layer)

    # process skins
    for layer in layer_list:
        layer.prepare_skins()

        if config.useSupport:
            layer.prepare_support()

    for layer in layer_list:
        layer.process_skins()
        layer.process_infill()


    if config.useSupport:
        for layer_index in reversed(range(len(layer_list))):
            one_last_layer_index = layer_index - 1
            if layer_index == 0:
                break
            layer_list[one_last_layer_index].support_required_ps = layer_list[layer_index].process_support()

        if config.one_empty_layer_between_support_and_model:
            for layer_index in range(len(layer_list)):
                one_above_layer_index = layer_index + 1
                if layer_index == len(layer_list) - 1:
                    break


                this_layer_support_required_ps = layer_list[layer_index].support_required_ps 

                one_above_layer_ps = layer_list[one_above_layer_index].support_required_ps 

                last_layer_area = this_layer_support_required_ps.difference_with(one_above_layer_ps)
           
                this_layer_support_required_ps = this_layer_support_required_ps.difference_with(last_layer_area)
                layer_list[layer_index].support_required_ps = this_layer_support_required_ps


    if config.raft == True:
        raft_base = layer_list[0].get_raft_base()

        raft_layer = Raft_layer(True ,False, BBox, raft_base)
        layer_list.insert(0, raft_layer)
        raft_layer = Raft_layer(False ,False, BBox, raft_base)
        layer_list.insert(0, raft_layer)
        raft_layer = Raft_layer(False, True, BBox, raft_base)
        layer_list.insert(0, raft_layer)
        layer_list.insert(0, raft_layer)
        # layer_list.insert(0, raft_layer)


    return layer_list