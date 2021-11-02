"""Controller holding and managing HUE resources of type `light`."""
from __future__ import annotations

from typing import Optional, Tuple, Type

from ..models.feature import (
    ColorFeature,
    ColorPoint,
    ColorTemperatureFeature,
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

    async def turn_on(self, id: str, transition_time: int | None = None) -> None:
        """Turn on the light."""
        return await self.set_on(id, True, transition_time)

    async def turn_off(self, id: str, transition_time: int | None = None) -> None:
        """Turn off the light."""
        return await self.set_on(id, False, transition_time)

    async def set_on(
        self, id: str, powered: bool, transition_time: int | None = None
    ) -> None:
        """Turn on/off the light."""
        update_obj = Light(id=id, on=OnFeature(on=powered))
        if transition_time is not None:
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        await self._send_put(id, update_obj)

    async def set_brightness(
        self, id: str, brightness: float, transition_time: int | None = None
    ) -> None:
        """Set brightness to light. Turn on light if it's currently off."""
        light = self[id]  # will raise keyerror if id not found
        update_obj = Light(id=id, dimming=DimmingFeature(brightness=brightness))
        if transition_time is not None:
            assert transition_time > 100
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        if not light.is_on:
            update_obj.on = OnFeature(on=True)
        await self._send_put(id, update_obj)

    async def set_color(
        self, id: str, x: float, y: float, transition_time: int | None = None
    ) -> None:
        """Set color to light. Turn on light if it's currently off."""
        light = self[id]  # will raise keyerror if id not found
        update_obj = Light(id=id, color=ColorFeature(xy=ColorPoint(x, y)))
        if transition_time is not None:
            assert transition_time > 100
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        if not light.is_on:
            update_obj.on = OnFeature(on=True)
        await self._send_put(id, update_obj)

    async def set_color_temperature(
        self, id: str, mirek: int, transition_time: int | None = None
    ) -> None:
        """Set Color Temperature to light. Turn on light if it's currently off."""
        light = self[id]  # will raise keyerror if id not found
        update_obj = Light(
            id=id, color_temperature=ColorTemperatureFeature(mirek=mirek)
        )
        if transition_time is not None:
            assert transition_time > 100
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        if not light.is_on:
            update_obj.on = OnFeature(on=True)
        await self._send_put(id, update_obj)

    async def set_state(
        self,
        id: str,
        on: bool = True,
        brightness: Optional[float] = None,
        color_xy: Optional[Tuple[float, float]] = None,
        color_temp: Optional[int] = None,
        transition_time: int | None = None,
    ) -> None:
        """Set multiple features to light at once."""
        update_obj = Light(id=id, on=OnFeature(on=on))
        if brightness is not None:
            update_obj.dimming = DimmingFeature(brightness=brightness)
        if color_xy is not None:
            update_obj.color = ColorFeature(xy=ColorPoint(*color_xy))
        if color_temp is not None:
            update_obj.color_temperature = ColorTemperatureFeature(mirek=color_temp)
        if transition_time is not None:
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        await self._send_put(id, update_obj)
