<<<<<<< 6d6de46bb3d2d3d466b6454f4043183da3c96cf5
import slicer.base_config as base_config
import sys

def reset():
    this_config = sys.modules["slicer.config"]
    attributes = dir(base_config)
    for atr in attributes:
        setattr(this_config,atr, getattr(base_config,atr))

# these parameters are here only for autocompletion,
#  they will be overwritten with default configuration and personnal configuration
layerThickness = None
line_width = None
temperature =  None
inAirSpeed = None
retractionSpeed = None
retractionLength = None
speedRate =  None
filamentDiameter = None
shellSize = None
firstLayerOffset = None
infillSpeed  = None
supportSpeed = None
skinSpeed = None
raftSpeed = None
boundarySpeed = None
holeSpeed = None
shellSpeed = None
min_retraction_distance = None
default_fan_speed = None
hasControllableFanSpeed  = None
useAdaptiveSlicing = None
useSupport = None
exteriorFanSpeed = None
bridgeFanSpeed = None
interiorFanSpeed = None
supportFanSpeed = None
upSkinsCount = None
downSkinsCount = None
supportSamplingDistance = None
supportOverhangangle = None # cos(155), 75 degree to building direction requires support
platform_bound = None
platform_bound_count = None
raft = None
raftLayerThickness = None
extrusion_multiplier = None
=======
import numpy as np

layerThickness = 0.2
line_width = 0.4
temperature =  210
inAirSpeed = 9000
retractionSpeed = 2400
retractionLength = 4.5
speedRate =  3000
filamentDiameter = 2.85
shellSize = 3
firstLayerOffset = 0
infillSpeed  = 1800
supportSpeed = 1800
skinSpeed = 1800
boundarySpeed = 1800
holeSpeed = 1800
shellSpeed = 1800
min_retraction_distance = 5
default_fan_speed = 0.5
hasControllableFanSpeed  = True
useAdaptiveSlicing = False
useSupport = True
exteriorFanSpeed = 0.4
bridgeFanSpeed = 1
interiorFanSpeed = 1
supportFanSpeed = 0.4
upSkinsCount = 4
downSkinsCount = 3
supportSamplingDistance = 1.5
link_threshold = np.sqrt(2*(supportSamplingDistance**2))
supportOverhangangle = -0.7 # cos(155), 75 degree to building direction requires support
platform_bound = "skirt"
platform_bound_count = 4
>>>>>>> sup
