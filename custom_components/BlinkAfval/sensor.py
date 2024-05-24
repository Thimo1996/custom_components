import aiohttp
import asyncio
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

URL = "https://www.mijnblink.nl/rest/adressen/1652200000015834/kalender/2024"

async def async_setup_entry(hass, config_entry, async_add_entities):
    session = async_get_clientsession(hass)

    async def async_fetch_data():
        async with session.get(URL) as response:
            if response.status != 200:
                raise UpdateFailed(f"Error fetching data: {response.status}")
            data = await response.json()
            for item in data:
                if item.get("afvalstroom_id") == 4:
                    return item.get("ophaaldatum")
            return None

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="my_custom_component",
        update_method=async_fetch_data,
        update_interval=timedelta(hours=1),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([MyCustomSensor(coordinator)], True)

class MyCustomSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Afvalstroom Ophaaldatum"
        self._attr_native_value = None

    @property
    def native_value(self):
        return self.coordinator.data

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()
