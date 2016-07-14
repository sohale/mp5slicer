from slicer.print_tree.layer import Layer
from slicer.print_tree.raft_layer import Raft_layer

def generate_tree(polygon_layers, BBox , support_polylines_list):
    import slicer.config.config as config

    layer_list = []



    for layer_index in range(len(polygon_layers)):
        if config.useSupport:
            layer = Layer(layer_list ,polygon_layers ,layer_index ,BBox ,support_polylines_list[layer_index])
        else:
            layer = Layer(layer_list ,polygon_layers ,layer_index ,BBox)
        layer_list.append(layer)


    # process skins
    for layer in layer_list:
        layer.prepare_skins()

    for layer in layer_list:
        layer.process_skins()
        layer.process_infill()

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