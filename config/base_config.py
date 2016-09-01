import numpy as np

layerThickness = 0.2
nozzle_size = 0.4 # for calculation extrusion
line_width = 0.4 # for caluculating the offset for polygons
extruder_temperature =  210
bed_temperature = 70
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
useAdaptiveSlicing = False
upSkinsCount = 4
downSkinsCount = 3

# fan speed
hasControllableFanSpeed  = True
default_fan_speed = 1
exteriorFanSpeed = 1
bridgeFanSpeed = 1
interiorFanSpeed = 1
supportFanSpeed = 1
skirtFanSpeed = 1
raftFanSpeed = 1

# support
useSupport = True
supportSamplingDistance = 2
link_threshold = 5*np.sqrt(2*(supportSamplingDistance**2))
bed_support_strengthen_offset_number = 2
bed_support_strengthen_layer_number = 2
supportOverhangangle = 85
support_horizontal_offset_from_parts = 0.4
support_area_enlarge_value = 0.4
one_empty_layer_between_support_and_model = True
support_line_angle = 0
does_remove_small_area = True
small_area = 5

platform_bound = "brim"
platform_bound_count = 3
raft = False
raftLayerThickness = 0.15
extrusion_multiplier = 1.1
initial_extrusion = 0.2
toFile = False

# outline / boundary
outline_outside_in = False
boundary_starts_close_to_point = [150, 300]
inner_boundary_coast_at_end_length = 0.5
outer_boundary_coast_at_end_length = 0
boundary_retraction_inside = True

# new
z_movement_speed = 9000
retraction_at_change_layer = True

# first layer
first_layer_line_width = 0.42
first_layer_infillSpeed = 750
first_layer_skinSpeed = 750
first_layer_boundarySpeed = 750 
first_layer_holeSpeed = 750
first_layer_supportSpeed = 750
first_layer_raftSpeed = 750
first_layer_shellSpeed = 750
first_layer_thickness = 0.2 # only allow maximun two decimal places