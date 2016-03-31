import numpy as np

def rotation_matrix(axis, theta):
        '''
        Generate a rotation matrix to Rotate the matrix over the given axis by
        the given theta (angle)
        Uses the Euler-Rodrigues formula for fast rotations:
        `https://en.wikipedia.org/wiki/Euler%E2%80%93Rodrigues_formula`_
        :param numpy.array axis: Axis to rotate over (x, y, z)
        :param float theta: Rotation angle in radians, use `math.radians` to
        convert degrees to radians if needed.
        '''
	axis = np.asarray(axis)
        # No need to rotate if there is no actual rotation
	if not axis.any():
		return np.zeros((3, 3))

        theta = np.asarray(theta)
        theta /= 2.

        axis = axis / np.sqrt(np.dot(axis, axis))

        a = np.cos(theta)
        b, c, d = - axis * np.sin(theta)
        angles = a, b, c, d
        powers = [x * y for x in angles for y in angles]
        aa, ab, ac, ad = powers[0:4]
        ba, bb, bc, bd = powers[4:8]
        ca, cb, cc, cd = powers[8:12]
        da, db, dc, dd = powers[12:16]

        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def rotate(mesh, axis, theta, point=None):
        '''
        Rotate the matrix over the given axis by the given theta (angle)
        Uses the `rotation_matrix`_ in the background.
        :param numpy.array axis: Axis to rotate over (x, y, z)
        :param float theta: Rotation angle in radians, use `math.radians` to
        convert degrees to radians if needed.
        :param numpy.array point: Rotation point so manual translation is not
        required
        '''
        # No need to rotate if there is no actual rotation
        if not theta:
            return mesh

        point = np.asarray(point or [0] * 3)
        rot_matrix = rotation_matrix(axis, theta)

        # No need to rotate if there is no actual rotation
        if not rot_matrix.any():
            return mesh

        def _rotate(matrix):
            if point.any():
                # Translate while rotating
                return (matrix + point).dot(rot_matrix) - point
            else:
                # Simply apply the rotation
                return matrix.dot(rot_matrix)
	
	rotated_matrix = np.zeros(mesh.shape)
	for i in range(3):
		rotated_matrix[:,i] = _rotate(mesh[:, i])
	

	return rotated_matrix

