from slicer.print_tree.layer import Layer
from slicer.print_tree.raft_layer import RaftLayer
import slicer.config.config as config


def generate_tree(polygon_layers, bounding_box):

    layer_list = []
    for layer_index in range(len(polygon_layers)):
        layer = Layer(layer_list, polygon_layers, layer_index, bounding_box)
        layer_list.append(layer)

    # process skins
    for layer in layer_list:
        layer.prepare_skins()

        if config.USE_SUPPORT:
            layer.prepare_support()

    for layer in layer_list:
        layer.process_skins()
        layer.process_infill()

    # change the following logic to somewhere else
    if config.USE_SUPPORT:
        for layer_index in reversed(range(len(layer_list))):
            one_last_layer_index = layer_index - 1
            if layer_index == 0:
                break
            layer_list[one_last_layer_index].support_required_ps = \
                layer_list[layer_index].process_support()

        if config.ONE_EMPTY_LAYER_BETWEEN_SUPPORT_AND_MODEL:
            for layer_index in range(len(layer_list)):
                one_above_layer_index = layer_index + 1
                if layer_index == len(layer_list) - 1:
                    break

                this_layer_support_required_ps = \
                    layer_list[layer_index].support_required_ps

                one_above_layer_ps = \
                    layer_list[one_above_layer_index].support_required_ps

                last_layer_area = \
                    this_layer_support_required_ps.difference_with(one_above_layer_ps)

                this_layer_support_required_ps = \
                    this_layer_support_required_ps.difference_with(last_layer_area)

                layer_list[layer_index].support_required_ps = \
                    this_layer_support_required_ps

    if config.RAFT is True:
        raft_base = layer_list[0].get_raft_base()
        raft_layer = RaftLayer(True, False, bounding_box, raft_base)
        layer_list.insert(0, raft_layer)
        raft_layer = RaftLayer(False, False, bounding_box, raft_base)
        layer_list.insert(0, raft_layer)
        raft_layer = RaftLayer(False, True, bounding_box, raft_base)
        layer_list.insert(0, raft_layer)
        layer_list.insert(0, raft_layer)
        # layer_list.insert(0, raft_layer)

    return layer_list
