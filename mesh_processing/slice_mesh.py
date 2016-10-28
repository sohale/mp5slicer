from mp5slicer.mesh_processing.mesh_operations import Mesh as MPmesh
from mp5slicer.mesh_processing.slice import adaptive_slicing, \
    slicer_from_mesh_as_dict
from slicer.commons.utils import polygonize_layers_from_trimed_dict, \
    scale_list_to_clipper


def move_to_center(mesh):
    import slicer.config.config as config
    bounding_box = mesh.bounding_box()
    platform_center = {}
    if config.ORIGIN == "center":
        platform_center["x"] = 0
        platform_center["y"] = 0
    else:
        platform_center["x"] = config.BUILD_PLATFORMX / 2
        platform_center["y"] = config.BUILD_PLATFORMX / 2
    objet_center = {}
    objet_center["x"] = (bounding_box.xmax - bounding_box.xmin)/2
    objet_center["y"] = (bounding_box.ymax - bounding_box.ymin)/2
    objet_center["x"] += bounding_box.xmin
    objet_center["y"] += bounding_box.ymin
    x_slide = platform_center["x"] - objet_center["x"]
    y_slide = platform_center["y"] - objet_center["y"]
    mesh.translate([x_slide, y_slide, 0])


def slice_mesh(stl_mesh):

    import slicer.config.config as config

    this_mesh = MPmesh(stl_mesh.vectors, fix_mesh=True)

    move_to_center(this_mesh)

    # this_mesh.translate([90,130,0])
    bounding_box = this_mesh.bounding_box()

    if config.USE_ADAPTIVE_SLICING:
        adaptive_height_list, adaptive_thickness = adaptive_slicing(
            this_mesh, config.LAYER_THICKNESS, curvature_tol=0.6,
            cusp_height_tol=0.15, layer_thickness_choices=[0.2, 0.15, 0.1],
            does_visualize=False)

        slice_layers = slicer_from_mesh_as_dict(
            this_mesh,
            slice_height_from=bounding_box.zmin,
            slice_height_to=bounding_box.zmax,
            slice_step=config.LAYER_THICKNESS,
            sliceplanes_height=adaptive_height_list)
    else:
        slice_layers = slicer_from_mesh_as_dict(
            this_mesh,
            slice_height_from=bounding_box.zmin,
            slice_height_to=bounding_box.zmax,
            slice_step=config.LAYER_THICKNESS)

    layers_as_polygons = polygonize_layers_from_trimed_dict(slice_layers)

    for layer_index in range(len(layers_as_polygons)):
        # scale test
        layers_as_polygons[layer_index] = scale_list_to_clipper(
            layers_as_polygons[layer_index])

    if config.USE_ADAPTIVE_SLICING:
        return layers_as_polygons, this_mesh, bounding_box, adaptive_thickness
    else:
        return layers_as_polygons, this_mesh, bounding_box
