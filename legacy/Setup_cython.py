from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
  name = 'slicerCyth',
  ext_modules = cythonize("slicerCyth.pyx"),
  include_dirs=[numpy.get_include()]
)