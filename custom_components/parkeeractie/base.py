from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ParkeeractieCoordinator


class BaseCoordinatorEntity(CoordinatorEntity[ParkeeractieCoordinator]):
    """Gedeelde basis voor alle Parkeeractie-entiteiten (device info, etc.)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ParkeeractieCoordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Mijn Parkeeractie",
            manufacturer="ARS T&TT",
            model="Start Stop Parking",
        )

    @property
    def entry_id(self) -> str:
        return self._entry.entry_id
