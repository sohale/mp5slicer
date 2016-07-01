
import numpy as np

from stl import mesh
import slicer


stl_mesh = mesh.Mesh.from_file('elephant.stl')
    # assume the center of the mesh are at (0,0)
    # translate x by 70 
stl_mesh.vectors[:,:,0]+=70
    # translate y by 70
stl_mesh.vectors[:,:,1]+=70
slice_layers = slicer.slicer_from_mesh(stl_mesh, 
                            slice_height_from=0.3, 
                            slice_height_to=stl_mesh.max_[2], 
                            slice_step=0.2)

def layer_raytrace(layer, ray_sep=0.5, direction_x=True):
	# This code can be vectorised to compute the rays at each height
	# simultaneously but it turns out to be quite difficult to do
	# (due to the fact that the number of polylines in each layer isn't constant)
	# and likely not worth the effort (as the speed-up from the vectorisation
	# competes with the overhead of dealing with the polylines issue.)  

	flip0 = int(direction_x) # direction of rays (const x or const y)
	flip1 = int(not flip0)

	layer_xy = np.asarray(layer)[:,:,:2] # xy coords of layer (trim z)

	lim = (np.max(layer_xy[:,:,flip0].flatten()) - 0.5, np.min(layer_xy[:,:,flip0].flatten()) + 0.5)
	# bounding values of coords in direction of rays (with offset).

	# coords of rays
	infill_range = np.linspace(lim[1], lim[0], np.ceil((lim[0] - lim[1]) / ray_sep) )	
	
	# sort points by max/min
	max_1, min_1 = np.max(layer_xy[:,:,flip0], axis=1), np.min(layer_xy[:,:,flip0], axis=1)
	max_2, min_2 = np.max(layer_xy[:,:,flip1], axis=1), np.min(layer_xy[:,:,flip1], axis=1) 
	delta_2 = max_2 - min_2 # find seperations
	delta_1 = max_1 - min_1
	
	layer_intersections = []
	for ray in infill_range:
		# mask for points which intersect with segments	
		mask = np.prod(layer_xy[:,:,flip0] - ray, axis=1) < 0
		
		# intercept points
		intercepts = np.sort( min_2[mask] + delta_2[mask]* (delta_1[mask] / (ray - min_1[mask])) )
	
		rays_and_intercepts = [ray, list(intercepts)]
		layer_intersections.append(rays_and_intercepts)
	
	return layer_intersections


import time
start = time.time()

lay = []
for index, layer in enumerate(slice_layers):
	
	switch = bool(index % 2)
	lay.append(layer_raytrace(layer, direction_x=switch))

print "This took %f" %(time.time() - start)

