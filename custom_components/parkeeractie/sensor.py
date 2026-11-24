"""Sensors for Parkeren Utrecht."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .base import ParkeeractieEntity
from .coordinator import ParkeeractieConfigEntry, ParkeeractieCoordinator

PARALLEL_UPDATES = 0


def hhmmss_to_seconds(raw: str | None) -> int | None:
    """Convert an HH:MM:SS string to seconds."""
    if not isinstance(raw, str):
        return None
    try:
        h, m, s = (int(x) for x in raw.split(":"))
    except ValueError:
        return None
    return h * 3600 + m * 60 + s


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ParkeeractieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors."""
    coordinator = entry.runtime_data
    async_add_entities([SaldoSensor(coordinator), TimeRemainingSensor(coordinator)])


class SaldoSensor(ParkeeractieEntity, SensorEntity):
    """Balance of the parking account."""

    _attr_translation_key = "saldo"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "EUR"
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: ParkeeractieCoordinator) -> None:
        super().__init__(coordinator, "saldo")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.saldo


class TimeRemainingSensor(ParkeeractieEntity, SensorEntity):
    """Remaining time of the active session or permit."""

    _attr_translation_key = "time_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: ParkeeractieCoordinator) -> None:
        super().__init__(coordinator, "time_remaining")

    @property
    def native_value(self) -> float:
        secs = hhmmss_to_seconds(self.coordinator.data.current_time)
        return 0 if secs is None else round(secs / 3600, 2)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        raw = self.coordinator.data.current_time
        return {
            "raw": raw or "00:00:00",
            "time_applicable": hhmmss_to_seconds(raw) is not None,
        }
