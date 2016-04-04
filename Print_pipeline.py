import Layer
def get_layer_list(polygon_layers):
    layer_list = []
    for layer_as_polygons in polygon_layers:
        layer = Layer(layer_as_polygons)
        layer_list.append(layer)
        for poly in layer_as_polygons:
            layer.add_island(poly)



    return layer_list


if __name__ == '__main__':

    polygon_layers = get_polygon_layers()
    layer_list = get_layer_list(polygon_layers)
    for layer in layer_list:
        g_buff.add_points(layer.G_print())