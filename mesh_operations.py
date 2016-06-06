import inspect, os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])

import numpy as np
from slicer.rotation import rotate as rotation
import decimal


class mesh():

    def __init__(self, input_triangles=[], input_normals=[], input_areas=[], fix_mesh=False):
        if len(input_triangles) == 0:
            raise ValueError

        self.triangles = np.asarray(input_triangles)


        if len(input_normals) != len(input_triangles):
            self.normals = self.compute_normals()
        else:
            self.normals = np.asarray(input_normals)

        if len(input_areas) != len(input_triangles):
            self.areas   = self.compute_areas()
        else:
            self.areas   = np.asarray(input_areas)

        if fix_mesh:
            self.remove_badtriangles()
            self.remove_duplicates()

        self.normalise_normals()
        self.sort_by_z()
        self.scale_to_int()
    #
    # def add_noise(self):
    #     noise = np.random.uniform(-1,0,self.triangles[:,:,0].size /3)
    #     self.triangles[:,:,0] = np.sum(self.triangles[:,:,2] , noise,

    def compute_normals(self):

        normal = np.cross(self.triangles[:,1] - self.triangles[:,0], self.triangles[:,2] - self.triangles[:,0])

        return normal


    def compute_areas(self):

        areas = 0.5 * np.sqrt((self.normals ** 2).sum(axis=1))
        areas = areas.reshape((areas.size, 1))

        return areas

    def normalise_normals(self):

        normal_len = np.sqrt(self.normals[:,0]**2 + self.normals[:,1]**2 + self.normals[:,2]**2)
        self.normals = ((self.normals / normal_len[:,None]) * 1000).astype(int)

    def sort_by_z(self, reverse=False):
        # Sort the triangles (normals) in order of ascending z
        # It may be the case that the triangles will already be sorted this way,
        # but if not it will be useful to put them in this form.

        min_z_order = np.argsort(np.amin(self.triangles[:,:,2], axis=1))
        # index of minimum z coord of each triangle
        if reverse:
            min_z_order = min_z_order[::-1]
            
        self.index_all(min_z_order)


    def remove_duplicates(self):
        # Remove any duplicate faces and their normals.

        # no two triangles can have the same centroid.
        centroids = self.triangles.sum(axis=1)

        # sort the list of centroids
        indices = np.lexsort(centroids.T)

        # find any duplicates (this returns the indices where the ANY of the points are different)
        diff = np.any(centroids[indices[1:]] != centroids[indices[:-1]], axis=1)

        mask = np.sort(indices[np.concatenate(([True], diff))])
        # return the unique triangles. The True will return at least the input list,
        # the sort returns the triangles in the order they were entered.

        self.index_all(mask)

    def remove_badtriangles(self):
        # Remove triangles which span 0 area
        # (i.e. triangles with duplicate vertices or points
        # which are co-linear). Written out in long-hand to save
        # looping through the triangles

        v = self.triangles[:,1] - self.triangles[:,0]
        w = self.triangles[:,2] - self.triangles[:,0]

        areax2 = np.linalg.norm(np.cross(v, w), axis=1)
        # this is the area of the parrellelepiped spanned
        # by two sides of the triangle, and therefore
        # twice the area of the triangle

        mask = [areax2 != 0]
        self.index_all(mask)


    def scale_to_int(self):
        # We presume that the triagnles are in units of mm and scale them to ints with units of micrometres
        # this makes checking equalities easier.
        # The areas are unaltered, meaning that they are no longer in the same units are the triangles.
        # this doesn't seem very important at the moment.
        self.triangles = (self.triangles).astype(dtype= np.dtype(float))

    def rotate(self, axis, theta):

        rot_triangles = rotation(self.triangles, axis, theta)

        return mesh(input_triangles=rot_triangles, input_areas=self.areas)

    def index_all(self, indices):
        # apply indexing to tris, norms, and areas

        self.triangles = self.triangles[indices]
        self.normals   = self.normals[indices]
        self.areas     = self.areas[indices]

    def bounding_box(self):
        # Returns a tuple of (max, min) for each of (x,y,z)

        bbox = bounding_box(np.min(self.triangles[:,:,0]),
                            np.max(self.triangles[:,:,0]),
                            np.min(self.triangles[:,:,1]),
                            np.max(self.triangles[:,:,1]),
                            np.min(self.triangles[:,:,2]),
                            np.max(self.triangles[:,:,2])
                            )

        return bbox

    def translate(self, translation):
        # Apply a given translation vector to the mesh

        self.triangles[:,:,0] += translation[0]
        self.triangles[:,:,1] += translation[1]
        self.triangles[:,:,2] += translation[2]

class bounding_box():
    def __init__(self,xmin,xmax,ymin,ymax,zmin,zmax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax





if __name__ == '__main__':

    from stl import mesh as np_mesh
    import mesh_operations

    stl_mesh = np_mesh.Mesh.from_file("elephant.stl")

    our_mesh = mesh(stl_mesh.vectors, fix_mesh=True)
