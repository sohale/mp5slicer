from .ohtake_belyaev_demo_subdivision_projection_qem import *

mesh_correction = False
writing_test_file = False
B = 1000000L


def demo_combination_plus_qem():

    from example_objects import make_example_vectorized
    object_name = "cube_example"  # "sphere_example" #or "rcube_vec" work well #"ell_example1"#"cube_with_cylinders"#"ell_example1"  " #"rdice_vec" #"cube_example"
    iobj = make_example_vectorized(object_name)

    (RANGE_MIN, RANGE_MAX, STEPSIZE) = (-12, +12, 0.287) #this stepsize is the one we use to compare the result with the c++ code( same resolution)
    #(RANGE_MIN, RANGE_MAX, STEPSIZE) = (-3, +5, 0.2)
    if object_name == "cube_with_cylinders" or object_name == "twist_object" or object_name == "french_fries" or object_name == "rdice_vec" or object_name == "cyl4" or object_name == "rods" or object_name == "bowl_15_holes":
        VERTEX_RELAXATION_ITERATIONS_COUNT = 1

    if object_name == "cyl4":
        (RANGE_MIN, RANGE_MAX, STEPSIZE) = (-32 / 2, +32 / 2, 1.92 / 4.0)

    elif object_name == "french_fries" or object_name == "rods":
        (RANGE_MIN, RANGE_MAX, STEPSIZE) = (-3, +5, 0.11)  # 0.05

    elif object_name == "bowl_15_holes":
        (RANGE_MIN, RANGE_MAX, STEPSIZE) = (-3, +5, 0.10)

    elif object_name == "cyl3":
        (RANGE_MIN, RANGE_MAX, STEPSIZE) = (-32 / 2, +32 / 2, 1.92 / 4.0)

    elif object_name == "cyl1":
        (RANGE_MIN, RANGE_MAX, STEPSIZE) = (-16, +32, 1.92 * 0.2 * 10 / 2.0)

    elif object_name == "cyl2":
        (RANGE_MIN, RANGE_MAX, STEPSIZE) = (-32, +32, 1.92 / 4.0 * 1.5 / 1.5)

    from stl_tests import make_mc_values_grid
    gridvals = make_mc_values_grid(iobj, RANGE_MIN, RANGE_MAX, STEPSIZE, old=False)
    vertex, faces = vtk_mc(gridvals, (RANGE_MIN, RANGE_MAX, STEPSIZE))
    print("MC calculated.")
    sys.stdout.flush()



    return m2stl_mesh(vertex, faces)

    # display_simple_using_mayavi_2([(vertex_before_qem, faces), (new_vertex_qem, faces), ],
    #    pointcloud_list=[],
    #    mayavi_wireframe=[False, False], opacity=[0.4*0, 1, 0.9], gradients_at=None, separate=False, gradients_from_iobj=None,
    #    minmax=(RANGE_MIN, RANGE_MAX))


def m2stl_mesh(verts, faces):
    from stl import mesh
    fv = verts[faces, :]
    print(fv.shape)

    data = np.zeros(fv.shape[0], dtype=mesh.Mesh.dtype)
    for i in range(fv.shape[0]):
        facet = fv[i]
        data['vectors'][i] = facet

    m = mesh.Mesh(data)
    return m