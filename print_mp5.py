import inspect
import os
import sys

sys.path.append(os.path.split(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))[0])
from slicer.implicit_slicing.mp5tostl import demo_combination_plus_qem
from slicer.Print_pipeline import print_from_stl
from stl import mesh


stl = demo_combination_plus_qem()
# iobj = json2implicit_func(json)
# iobj.implicitGradient(x)
# iobj.implicitFunction(x)
# stl = demo_combination_plus_qem(iobj)
stl.save("mp5.stl")
print_from_stl(stl)
# g = slice(stl, iobj)


