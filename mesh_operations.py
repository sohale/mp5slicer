import numpy as np
from rotation import rotate as rotation
import decimal

class mesh():

	def __init__(self, input_triangles=0, input_normals=0, input_areas=0, fix_mesh=False):
		if type(input_triangles) == int:
			return "Input mesh required"


		self.triangles = np.asarray(input_triangles)

		if type(input_normals) == int:
			self.normals = self.compute_normals()
		else:
			self.normals = np.asarray(input_normals)

		if type(input_areas) == int:
			self.areas   = self.compute_areas()
		else:
			self.areas   = np.asarray(input_areas)

		if fix_mesh:
			self.remove_badtriangles()
		 	self.remove_duplicates()
	
		self.normalise_normals()
		self.sort_by_z()
		self.scale_to_int()


	def compute_normals(self):

		normal = np.cross(self.triangles[:,1] - self.triangles[:,0], self.triangles[:,2] - self.triangles[:,0])

        	return normal


	def compute_areas(self):

		areas = 0.5 * np.sqrt((self.normals ** 2).sum(axis=1))
        	areas = areas.reshape((areas.size, 1))

        	return areas

	def normalise_normals(self):

		normal_len = np.sqrt(self.normals[:,0]**2 + self.normals[:,1]**2 + self.normals[:,2]**2)
		self.normals = self.normals / normal_len[:,None]

	def sort_by_z(self):
        	# Sort the triangles (normals) in order of ascending z
        	# It may be the case that the triangles will already be sorted this way,
        	# but if not it will be useful to put them in this form.

        	min_z_order = np.argsort(np.amin(self.triangles[:,:,2], axis=1))
    		# index of minimum z coord of each triangle

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

		areax2 = np.cross(v, w) 
		# this is the area of the parrellelepiped spanned
		# by two sides of the triangle, and therefore
		# twice the area of the triangle

		mask = [areax2 != 0]

		self.index_all(mask)
		

	def scale_to_int(self):

	        # This function returns the points and normals as ints with 5 digits of precision
		# throwing away some (irrelevant) precision to make checking equalities easier
		# both are rounded to different tolerances, changing their units. 
		# the areas are unaltered, meaning that they are no longer in the same units are the triangles.
		# this doesn't seem very important at the moment.
		self.triangles = (self.triangles / 10**(np.floor(np.log10(np.abs(np.max(self.triangles)))) - 5)).astype(int)
	
		self.normals   = (self.normals / 10**(np.floor(np.log10(np.abs(np.max(self.normals)))) - 5)).astype(int)
	

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
		
		x_max_min = (np.max(self.triangles[:,:,0]),  np.min(self.triangles[:,:,0]))
		y_max_min = (np.max(self.triangles[:,:,1]),  np.min(self.triangles[:,:,1]))
		z_max_min = (np.max(self.triangles[:,:,2]),  np.min(self.triangles[:,:,2]))

		return (x_max_min, y_max_min, z_max_min)

	def translate(self, translation):
		# Apply a given translation vector to the mesh
	
		self.triangles[:,:,0] += translation[0]
		self.triangles[:,:,1] += translation[1]
		self.triangles[:,:,2] += translation[2]


