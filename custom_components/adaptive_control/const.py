"""Constants for adaptive_control."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "adaptive_control"

# Configuration Keys
CONF_NAME = "name"
CONF_INPUT_SENSOR = "input_sensor"
CONF_OUTPUT_ENTITY = "output_entity"
CONF_MIN_VALUE = "min_value"
CONF_MAX_VALUE = "max_value"
CONF_TARGET = "target"
CONF_RLS_FORGETTING = "rls_forgetting"
CONF_CONTROL_REGULARIZATION = "control_regularization"

# Defaults
DEFAULT_MIN_VALUE = 0
DEFAULT_MAX_VALUE = 100
DEFAULT_TARGET = 0
DEFAULT_RLS_FORGETTING = 0.99
DEFAULT_CONTROL_REGULARIZATION = 0.5
