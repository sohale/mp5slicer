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
        # this function change layer in layer list in place
        from slicer.print_tree.support import generate_support_from_layer_list
        generate_support_from_layer_list(layer_list)

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
