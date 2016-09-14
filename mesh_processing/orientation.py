import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from stl import mesh as stl_np_mesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import self_support_detection
import numpy as np
import mesh_operations

test_file = 'weird.stl'

test_file = '../stl_files/Misfit_180_HS1177_Camera_Mount.stl'

# Read in mesh
stl_input = stl_np_mesh.Mesh.from_file(test_file)

stl_mesh = mesh_operations.mesh(stl_input.vectors)

stl_mesh_side = stl_mesh.rotate([0, 1, 0], np.pi/4.)


def optimise_orientation(stl_mesh):

    # Remove duplicate normals
    order = np.lexsort(stl_mesh.normals.T)

    stl_mesh.index_all(order)
    # the index_all method takes a set of indices and applies them to
    # all of the attributes of stl_mesh

    diff = np.diff(stl_mesh.normals, axis=0)
    ui = np.ones(len(stl_mesh.normals), 'bool')

    ui[1:] = (diff != 0).any(axis=1)

    unique_norms = stl_mesh.normals[ui]
    # Now we have only the unique normals

    facets = np.bincount(ui.cumsum()-1, stl_mesh.areas.flatten())
    # This line sums the area of all triangles which have the same normal
    # These are the indices of the facets (indices which match the order of normals_int and triangles_int)
    facets_area_indx = np.argsort(facets)[::-1]
    unique_norms = unique_norms[facets_area_indx]
    # order the unique norms by the amount of area they correspond to.

    z = [0, 0, -1]  # down

    score = []
    orientation_vector = []
    base_area = [0]  # initialise this with a zero, this will be removed later.
    for direction in unique_norms[:10]:

        rotation_vector = np.cross(direction, z)

        rotation_angle = np.arccos(
            np.dot(direction, z) / np.sqrt(direction[0]**2 +
                                           direction[1]**2 +
                                           direction[2]**2))

        # rotate the mesh into an orientation
        rotated_mesh = stl_mesh.rotate(rotation_vector, -rotation_angle)

        area = (rotated_mesh.areas[(rotated_mesh.triangles[:,:,2] < 1.01*rotated_mesh.triangles[0,0,2]).all(axis=1)]).sum()
        # find the area of the base in this orientation

        if area > max(base_area)/2:
            # since the support check is expensive we only do it for bases
            # which are at least half the size of the maximum base.
            support_output = self_support_detection.support_areas_and_volume(
                rotated_mesh)
            score.append(area - support_output[2]/10000)

            orientation_vector.append(direction)

        base_area.append(area)

    optimal_orientation = unique_norms[base_area.index(max(base_area))]

    rotation_vector = np.cross(optimal_orientation, z)

    rotation_angle = np.arccos(
        np.dot(optimal_orientation, z) / np.sqrt(optimal_orientation[0]**2 +
                                                 optimal_orientation[1]**2 +
                                                 optimal_orientation[2]**2))

    return stl_mesh.rotate(rotation_vector, -rotation_angle)


def display_using_matplotlib(triangles):

        """ Displays vertices, centroids (optional) and normal vectors """
        # Display resulting triangular mesh using Matplotlib.
        # Display the centroids
        # Display the normal vectors at centroids

    fig = plt.figure(figsize=(10, 12))
    ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(np.amin(triangles[:,:,0]), np.amax(triangles[:,:,0]))
        ax.set_ylim(np.amin(triangles[:,:,1]), np.amax(triangles[:,:,1]))
        ax.set_zlim(np.amin(triangles[:,:,2]), np.amax(triangles[:,:,2]))
   
    

        # Fancy indexing: `verts[faces]` to generate a collection of triangles
        disp_mesh = Poly3DCollection(triangles, alpha=0.2)
        disp_mesh.set_facecolor([1, 0.5, 0.5])
        disp_mesh.set_linewidth(0.2)
        disp_mesh.set_antialiased(True)

        ax.add_collection3d(disp_mesh)
 
        plt.show()


output_mesh = optimise_orientation(stl_mesh) 

display_using_matplotlib(output_mesh.triangles)
