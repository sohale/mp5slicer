import numpy as np

layerThickness = 0.2
nozzle_size = 0.4 # for calculation extrusion
line_width = 0.4 # for caluculating the offset for polygons
temperature =  210
inAirSpeed = 9000
retractionSpeed = 2400
retractionLength = 4.5
speedRate =  1800
filamentDiameter = 2.85
shellSize = 3
firstLayerOffset = 0
infillSpeed  = 1800
skinSpeed = 1800
raftSpeed = 1800
boundarySpeed = 1800
holeSpeed = 1800
shellSpeed = 1800
supportSpeed = 1800
min_retraction_distance = 5
default_fan_speed = 0.5
hasControllableFanSpeed  = True
useAdaptiveSlicing = False
useSupport = True
exteriorFanSpeed = 0.3
bridgeFanSpeed = 0.4
interiorFanSpeed = 0
supportFanSpeed = 1
skirtFanSpeed = 0.2
raftFanSpeed = 0
upSkinsCount = 4
downSkinsCount = 3

# support
supportSamplingDistance = 2
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

# outline
coast_at_end_length = 0
outline_outside_in = False

# new
z_movement_speed = 9000
retraction_at_change_layer = True
boundary_starts_close_to_point = None

# first layer
first_layer_line_width = 0.44
first_layer_infillSpeed = 750
first_layer_skinSpeed = 750
first_layer_boundarySpeed = 750 
first_layer_holeSpeed = 750
first_layer_supportSpeed = 750
first_layer_raftSpeed = 750
first_layer_shellSpeed = 750