"""Coordinator for Parkeeractie integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ParkeeractieClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class ParkeeractieCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Parkeeractie data updates."""

    def __init__(self, hass: HomeAssistant, username: str, password: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        session = async_get_clientsession(hass)
        self._client = ParkeeractieClient(session, username, password)

    @property
    def client(self) -> ParkeeractieClient:
        """Return the API client."""
        return self._client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            saldo, current_time = await self._client.login_and_fetch()
        except Exception as err:
            raise UpdateFailed(str(err)) from err
        else:
            return {"saldo": saldo, "current_time": current_time}
