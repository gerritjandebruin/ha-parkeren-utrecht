"""Coordinator for Parkeren Utrecht."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from aiohttp import ClientError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ParkeeractieClient
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

type ParkeeractieConfigEntry = ConfigEntry[ParkeeractieCoordinator]


@dataclass(frozen=True, slots=True)
class ParkeeractieData:
    """Balance and remaining time of the account."""

    saldo: float | None
    current_time: str | None


class ParkeeractieCoordinator(DataUpdateCoordinator[ParkeeractieData]):
    """Logs in and fetches the account overview."""

    config_entry: ParkeeractieConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ParkeeractieConfigEntry,
        client: ParkeeractieClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> ParkeeractieData:
        try:
            saldo, current_time = await self.client.login_and_fetch()
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(str(err)) from err
        return ParkeeractieData(saldo=saldo, current_time=current_time)
