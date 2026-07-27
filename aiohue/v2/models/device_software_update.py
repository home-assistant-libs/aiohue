"""
Model(s) for device_software_update resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_software_update
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class DeviceSoftwareUpdateState(Enum):
    """
    Enum with the possible software update states of a device.

    no_update: no software update is known for the device.
    update_pending: an update is known but the transfer to the device did not
    start or complete yet, so it can not be installed.
    ready_to_install: the update is ready to be installed.
    installing: the update is being installed.
    """

    NO_UPDATE = "no_update"
    UPDATE_PENDING = "update_pending"
    READY_TO_INSTALL = "ready_to_install"
    INSTALLING = "installing"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return DeviceSoftwareUpdateState.UNKNOWN


@dataclass
class DeviceSoftwareUpdate:
    """
    Represent a (full) `DeviceSoftwareUpdate` resource when retrieved from the api.

    Provided by every device that supports software updates. The update itself is
    driven by the bridge, this resource only reports its progress.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_software_update_get
    """

    id: str
    owner: ResourceIdentifier
    state: DeviceSoftwareUpdateState
    # problems: conditions that block the update until the user resolves them,
    # e.g. `battery_low`. The api reference does not publish the possible values.
    problems: list[str]

    type: ResourceTypes = ResourceTypes.DEVICE_SOFTWARE_UPDATE
