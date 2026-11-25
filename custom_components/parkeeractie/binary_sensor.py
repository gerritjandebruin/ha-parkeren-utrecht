"""Binary sensors for Parkeren Utrecht."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .base import ParkeeractieEntity
from .coordinator import ParkeeractieConfigEntry, ParkeeractieCoordinator
from .sensor import hhmmss_to_seconds

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ParkeeractieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the binary sensors."""
    async_add_entities([ParkingProblemSensor(entry.runtime_data)])


class ParkingProblemSensor(ParkeeractieEntity, BinarySensorEntity):
    """On when there is no balance or no time left."""

    _attr_translation_key = "parking_problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: ParkeeractieCoordinator) -> None:
        super().__init__(coordinator, "parkeren_problem")

    @property
    def _reason(self) -> str:
        data = self.coordinator.data
        if (data.saldo or 0) <= 0:
            return "geen_geld"
        if not hhmmss_to_seconds(data.current_time):
            return "geen_tijd"
        return "geen"

    @property
    def is_on(self) -> bool:
        return self._reason != "geen"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "saldo": data.saldo,
            "current_time": data.current_time,
            "reason": self._reason,
        }
