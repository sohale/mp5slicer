from stl import mesh
import numpy as np


test_file = 'testcube_05mm.stl'
test_file = 'StanfordBunny_jmil_HIGH_RES_Smoothed.stl'


stl_mesh = mesh.Mesh.from_file(test_file)

def remove_badtriangles(triangles, normals):
	# Remove ill-defined triangles (and corresponding normals)
 	# (triangles which don't have 3 distinct points).
	
	# shift the points of each triangle by one
	shifted_triangles = np.roll(triangles, 1, axis=1)

	# subtract them from the other
	diff_shifted_triangles = (triangles - shifted_triangles)
	# for triangle (A,B,C) => ((A-B), (B-C), (C-A))

	# where this is zero two lines are the same.
	# if ALL of (x,y,z) are zero, for ANY of the coords then it's a bad triangle
	# and this gives a True 	
	mask = ((diff_shifted_triangles == 0).all(axis=2)).any(axis=1)

	# we want the triangles for whom the last line was False
	return triangles[mask == False], normals[mask == False]


def sort_by_z(triangles, normals):
	# Sort the triangles (normals) in order of ascending z
	# It may be the case that the triangles will already be sorted this way,
	# but if not it will be useful to put them in this form.

	min_z_order = np.argsort(np.amin(triangles[:,:,2], axis=1)) 
	# index of minimum z coord of each triangle
	
	return triangles[min_z_order], normals[min_z_order]


def remove_duplicates(triangles, normals):
	# Remove any duplicate faces and their normals.
	
	# no two triangles can have the same centroid.	
	centroids = triangles.sum(axis=1)
        
	# sort the list of centroids
	indices = np.lexsort(centroids.T)
        
	# find any duplicates (this returns the indices where the ANY of the points are different)
	diff = np.any(centroids[indices[1:]] != centroids[indices[:-1]], axis=1)

	mask = np.sort(indices[np.concatenate(([True], diff))])
	# return the unique triangles. The True will return at least the input list, 
	# the sort returns the triangles in the order they were entered.
	
	return triangles[mask], normals[mask]



import time
start_time = time.time()
remove_badtriangles(stl_mesh.vectors, stl_mesh.normals)

print("--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
sort_by_z(stl_mesh.vectors, stl_mesh.normals)

print("--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
remove_duplicates(stl_mesh.vectors, stl_mesh.normals)

print("--- %s seconds ---" % (time.time() - start_time))

