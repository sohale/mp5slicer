import sys

import slicer.config.base_config as base_config


def reset():
    this_config = sys.modules["slicer.config.config"]
    attributes = dir(base_config)
    for atr in attributes:
        setattr(this_config, atr, getattr(base_config, atr))

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
skirtFanSpeed = None
raftFanSpeed = None
upSkinsCount = None
downSkinsCount = None

supportSamplingDistance = None
supportOverhangangle = None 
link_threshold = None
bed_support_strengthen_number = None

platform_bound = None
platform_bound_count = None
raft = None
raftLayerThickness = None
extrusion_multiplier = None
initial_extrusion = None
crossArea = None
toFile = False