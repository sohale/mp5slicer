import slicer.base_config as base_config
import sys

def reset():
    this_config = sys.modules["slicer.config"]
    attributes = dir(base_config)
    for atr in attributes:
        setattr(this_config,atr, getattr(base_config,atr))


layerThickness = 0.2
line_width = 0.4
temperature =  220
inAirSpeed = 9000
retractionSpeed = 2400
retractionLength = 4.5
speedRate =  3000
filamentDiameter = 2.85
shellSize = 3
firstLayerOffset = 0
infillSpeed  = 3000
supportSpeed = 2400
skinSpeed = 2400
raftSpeed = 2000
boundarySpeed = 2400
holeSpeed = 2400
shellSpeed = 2400
min_retraction_distance = 5
default_fan_speed = 0.5
hasControllableFanSpeed  = True
useAdaptiveSlicing = False
useSupport = True
exteriorFanSpeed = 0.4
bridgeFanSpeed = 1
interiorFanSpeed = 0.4
supportFanSpeed = 0.4
upSkinsCount = 4
downSkinsCount = 3
supportSamplingDistance = 2
supportOverhangangle = -0.7 # cos(155), 75 degree to building direction requires support
platform_bound = "skirts"
platform_bound_count = 1
raft = False
raftLayerThickness = 0.2
extrusion_multiplier = 1.2
