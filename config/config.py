import sys
import slicer.config.base_config as base_config

if sys.version_info.major == 3 and sys.version_info.minor >= 5:
	# TODO : a new file for the types
	import typing
	from typing import NewType, List, Any
	angle = NewType('angle', float)
	option = NewType('option', List[Any])
	point2d = NewType('point2d', List[float])

class ConfigurationError(Exception):
    pass

def reset():
    this_config = sys.modules["slicer.config.config"]
    attributes = dir(base_config)
    for atr in attributes:
        setattr(this_config, atr, getattr(base_config, atr))

# these parameters are here only for autocompletion,
# they will be overwritten with default configuration
# and personnal configuration

LAYER_THICKNESS = None  # type: float
NOZZLE_SIZE = None  # type: float
LINE_WIDTH = None  # type: float
EXTRUDER_TEMPERATURE = None  # type: int
BED_TEMPERATURE = None  # type: int
RETRACTION_LENGTH = None  # type: float
FILAMENT_DIAMETER = None  # type: float
SHELL_SIZE = None  # type: int
FIRST_LAYER_OFFSET = None  # type: float
MIN_RETRACTION_DISTANCE = None  # type: float
USE_ADAPTIVE_SLICING = None  # type: bool
UP_SKINS_COUNT = None  # type: int
DOWN_SKINS_COUNT = None  # type: int

# travel speed
Z_MOVEMENT_SPEED = None  # type: int
IN_AIR_SPEED = None  # type: int
RETRACTION_SPEED = None  # type: int
SPEED_RATE = None  # type: int
INFILL_SPEED = None  # type: int
SKIN_SPEED = None  # type: int
RAFT_SPEED = None  # type: int
BOUNDARY_SPEED = None  # type: int
INNER_BOUNDARY_SPEED = None  # type: int
HOLE_SPEED = None  # type: int
SUPPORT_SPEED = None  # type: int

# fan speed
HAS_CONTROLLABLE_FAN_SPEED = None  # type: int
DEFAULT_FAN_SPEED = None  # type: int
EXTERIOR_FAN_SPEED = None  # type: int
BRIDGE_FAN_SPEED = None  # type: int
INTERIOR_FAN_SPEED = None  # type: int
SUPPORT_FAN_SPEED = None  # type: int
SKIRT_FAN_SPEED = None  # type: int
RAFT_FAN_SPEED = None  # type: int

# support
USE_SUPPORT = None  # type: bool
SUPPORT_SAMPLING_DISTANCE = None  # type: float
LINK_THRESHOLD = None  # type: float
BED_SUPPORT_STRENGTHEN_OFFSET_NUMBER = None  # type: int
BED_SUPPORT_STRENGTHEN_LAYER_NUMBER = None  # type: int
SUPPORT_OVERHANG_ANGLE = None  # type: angle
SUPPORT_HORIZONTAL_OFFSET_FROM_PARTS = None  # type: float
SUPPORT_AREA_ENLARGE_VALUE = None  # type: float
ONE_EMPTY_LAYER_BETWEEN_SUPPORT_AND_MODEL = None  # type: bool
SUPPORT_LINE_ANGLE = None  # type: angle
DOES_REMOVE_SMALL_AREA = None  # type: bool
SMALL_AREA = None  # type: float
BED_SUPPORT_STRENGTHEN_NUMBER = None  # type: int

PLATFORM_BOUND = None  # type: option
PLATFORM_BOUND_COUNT = None  # type: int
RAFT = None  # type: bool
RAFT_LAYER_THICKNESS = None  # type: float
EXTRUSION_MULTIPLIER = None  # type: float
INITIAL_EXTRUSION = None  # type: float
TO_FILE = None  # type: bool

# outline / boundary
OUTLINE_OUTSIDE_IN = None  # type: bool
BOUNDARY_STARTS_CLOSE_TO_POINT = None  # type: point2d
INNER_BOUNDARY_COAST_AT_END_LENGTH = None  # type: float
OUTER_BOUNDARY_COAST_AT_END_LENGTH = None  # type: float
BOUNDARY_RETRACTION_INSIDE = None  # type: bool

RETRACTION_AT_CHANGE_LAYER = None  # type: bool

# first layer
FIRST_LAYER_LINE_WIDTH = None  # type: float
FIRST_LAYER_INFILL_SPEED = None  # type: int
FIRST_LAYER_SKIN_SPEED = None  # type: int
FIRST_LAYER_HOLE_SPEED = None  # type: int
FIRST_LAYER_SUPPORT_SPEED = None  # type: int
FIRST_LAYER_RAFT_SPEED = None  # type: int
FIRST_LAYER_BOUNDARY_SPEED = None  # type: int
FIRST_LAYER_INNER_BOUNDARY_SPEED = None  # type: int
FIRST_LAYER_THICKNESS = None  # type: float

# for testing only
TEST_PARAMETER = None  # type: int


# TODO : change to legit parameter
BUILD_PLATFORMX = None  # type: int
BUILD_PLATFORMY = None  # type: int
ORIGIN = None  # type: option