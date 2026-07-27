"""
Model(s) for switch_input_configuration resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_switch_input_configuration
"""

from dataclasses import dataclass
from enum import Enum

from .feature import ConfigurationStatus
from .resource import ResourceIdentifier, ResourceTypes


class SwitchModeType(Enum):
    """
    Enum with the modes a configurable switch can operate in.

    A rocker mode pairs the physical inputs into on/off couples, a pushbutton
    mode exposes every physical input as its own button.
    """

    SWITCH_SINGLE_ROCKER = "switch_single_rocker"
    SWITCH_SINGLE_PUSHBUTTON = "switch_single_pushbutton"
    SWITCH_DUAL_ROCKER = "switch_dual_rocker"
    SWITCH_DUAL_PUSHBUTTON = "switch_dual_pushbutton"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return SwitchModeType.UNKNOWN


@dataclass
class SwitchMode:
    """
    Represent the mode a configurable switch operates in.

    Used by `switch_input_configuration` resources.
    """

    status: ConfigurationStatus
    mode: SwitchModeType
    # mode_values: the modes this particular switch supports.
    mode_values: list[SwitchModeType]


@dataclass
class SwitchModePut:
    """
    SwitchMode properties that can be set/updated with a PUT request.

    Used by `switch_input_configuration` resources.
    """

    mode: SwitchModeType


@dataclass
class SwitchInputConfiguration:
    """
    Represent a (full) `SwitchInputConfiguration` resource when retrieved from the api.

    Offered by devices with configurable switch modes and replaces the deprecated
    `device_mode` property on the device resource. Changing the mode changes which
    button resources the device exposes, listed here as `linked_services`.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_switch_input_configuration_get
    """

    id: str
    owner: ResourceIdentifier
    # linked_services: the button services that belong to the current mode,
    # empty while the bridge is still creating them.
    linked_services: list[ResourceIdentifier]

    switch_mode: SwitchMode | None = None

    type: ResourceTypes = ResourceTypes.SWITCH_INPUT_CONFIGURATION


@dataclass
class SwitchInputConfigurationPut:
    """
    SwitchInputConfiguration properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_switch_input_configuration__id__put
    """

    switch_mode: SwitchModePut | None = None
