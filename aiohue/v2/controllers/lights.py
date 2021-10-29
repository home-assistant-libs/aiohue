"""Controller holding and managing HUE resources of type `light`."""

from typing import Type

from aiohue.models.feature import (
    ColorFeature,
    ColorPoint,
    DimmingFeature,
    DynamicsFeature,
    OnFeature,
)

from ..models.light import Light
from ..models.resource import ResourceTypes
from .base import BaseResourcesController


class LightsController(BaseResourcesController[Type[Light]]):
    """Controller holding and managing HUE resources of type `light`."""

    item_type = ResourceTypes.LIGHT

    async def set_power(
        self, id: str, powered: bool, transition_time: int | None = None
    ) -> None:
        """Turn on/off the light."""
        update_obj = Light(id=id, on=OnFeature(on=powered))
        if transition_time is not None:
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        await self._send_put(id, update_obj)

    async def turn_on(self, id: str, transition_time: int | None = None) -> None:
        """Turn on the light."""
        return await self.set_power(id, True, transition_time)

    async def turn_off(self, id: str, transition_time: int | None = None) -> None:
        """Turn off the light."""
        return await self.set_power(id, False, transition_time)

    async def set_brightness(
        self, id: str, brightness: float, transition_time: int | None = None
    ) -> None:
        """Set brightness to light. raises exception if light does not support DimmingFeature."""
        update_obj = Light(id=id, dimming=DimmingFeature(brightness=brightness))
        if transition_time is not None:
            assert transition_time > 100
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        await self._send_put(id, update_obj)

    async def set_color(
        self, id: str, x: float, y: float, transition_time: int | None = None
    ) -> None:
        """Set color to light. raises exception if light does not support ColorFeature."""
        update_obj = Light(id=id, color=ColorFeature(xy=ColorPoint(x, y)))
        if transition_time is not None:
            assert transition_time > 100
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        await self._send_put(id, update_obj)
