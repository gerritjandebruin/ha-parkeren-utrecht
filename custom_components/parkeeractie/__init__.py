"""Parkeeractie integration for Home Assistant."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .coordinator import ParkeeractieCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

PLATFORMS: list[str] = ["sensor", "binary_sensor"]

# Service schemas
START_PARKING_SESSION_SCHEMA = vol.Schema(
    {
        vol.Required("license_plate"): cv.string,
        vol.Required("end_time"): cv.datetime,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Parkeeractie from a config entry."""
    coordinator = ParkeeractieCoordinator(
        hass,
        username=entry.data["username"],
        password=entry.data["password"],
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Register services
    async def start_parking_session(call: ServiceCall) -> None:
        """Service om een parkeerssessie te starten."""
        license_plate = call.data["license_plate"]
        end_time = call.data["end_time"]

        # Convert datetime to ISO string
        if isinstance(end_time, datetime):
            end_time_str = end_time.isoformat()
        else:
            end_time_str = str(end_time)

        # Use the coordinator's client to start the session
        success = await coordinator.client.start_parking_session(
            license_plate=license_plate, end_time=end_time_str
        )

        if success:
            # Refresh coordinator data to reflect the new session
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "start_parking_session",
        start_parking_session,
        schema=START_PARKING_SESSION_SCHEMA,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload parkeeractie integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        # Remove services if this was the last entry
        if not hass.data.get(DOMAIN):
            hass.services.async_remove(DOMAIN, "start_parking_session")

    return unload_ok
