import numpy as np

layerThickness = 0.2
line_width = 0.4
temperature =  220
inAirSpeed = 9000
retractionSpeed = 2400
retractionLength = 4.5
speedRate =  3000
filamentDiameter = 2.85
shellSize = 3
firstLayerOffset = 0.2
infillSpeed  = 5400
skinSpeed = 5400
raftSpeed = 2000
boundarySpeed = 5400
holeSpeed = 5400
shellSpeed = 5400
supportSpeed = 1800
min_retraction_distance = 5
default_fan_speed = 0.5
hasControllableFanSpeed  = True
useAdaptiveSlicing = False
useSupport = False
exteriorFanSpeed = 0.3
bridgeFanSpeed = 0.4
interiorFanSpeed = 0
supportFanSpeed = 1
skirtFanSpeed = 0.2
raftFanSpeed = 0
upSkinsCount = 4
downSkinsCount = 3

# support
supportSamplingDistance = 1.5
link_threshold = 5*np.sqrt(2*(supportSamplingDistance**2))
bed_support_strengthen_number = 5
supportOverhangangle = -0.7 # cos(155), 75 degree to building direction requires support

platform_bound = "brim"
platform_bound_count = 10
raft = False
raftLayerThickness = 0.15
extrusion_multiplier = 1.1
initial_extrusion = 0.2
toFile = False
boundary_finish_shorten_length = 1
