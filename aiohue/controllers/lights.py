"""Controller holding and managing HUE resources of type `light`."""

from typing import Type

from aiohue.models.feature import DimmingFeature, DynamicsFeature, OnFeature

from ..models.light import Light
from ..models.resource import ResourceTypes
from .base import BaseResourcesController


class LightsController(BaseResourcesController[Type[Light]]):
    """Controller holding and managing HUE resources of type `light`."""

    item_type = ResourceTypes.LIGHT

    async def turn_on(self, id: str) -> None:
        """Turn on the light."""
        await self.update(id, Light(id=id, on=OnFeature(on=True)))
        pass

    async def turn_off(self, id: str) -> None:
        """Turn off the light."""
        await self.update(id, Light(on=OnFeature(on=False)))

    async def set_brightness(
        self, id: str, brightness: float, duration: int | None = None
    ) -> None:
        """Set brightness to light. raises exception if light does not support DimmingFeature."""
        update_obj = Light(id=id, dimming=DimmingFeature(brightness=brightness))
        if duration is not None:
            update_obj.dynamics = DynamicsFeature(duration=duration)
        await self.update(id, update_obj)
