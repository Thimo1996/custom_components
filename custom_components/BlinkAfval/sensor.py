import aiohttp
import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    url = config_entry.data["url"]
    session = async_get_clientsession(hass)
    _LOGGER.debug(f"Setting up entry with URL: {url}")

    async def async_fetch_data():
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                data = await response.json()
                _LOGGER.debug(f"Fetched data: {data}")
                for item in data:
                    if item.get("afvalstroom_id") == 4:
                        _LOGGER.debug(f"Found matching item: {item}")
                        return item.get("ophaaldatum")
                _LOGGER.debug("No matching item found")
                return None
        except Exception as e:
            _LOGGER.error(f"Exception while fetching data: {e}")
            raise UpdateFailed(f"Error fetching data: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="my_custom_component",
        update_method=async_fetch_data,
        update_interval=timedelta(minutes=15),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([MyCustomSensor(coordinator)], True)
    _LOGGER.debug("Entities added")

class MyCustomSensor(SensorEntity):
    def __init__(self, coordinator):
        super().__init__()
        self.coordinator = coordinator
        self._attr_name = "Afvalstroom Ophaaldatum"
        self._attr_native_value = None

    @property
    def native_value(self):
        _LOGGER.debug(f"Getting native_value: {self.coordinator.data}")
        return self.coordinator.data

    @property
    def available(self):
        _LOGGER.debug(f"Checking availability: {self.coordinator.last_update_success}")
        return self.coordinator.last_update_success

    async def async_update(self):
        _LOGGER.debug("Requesting refresh")
        await self.coordinator.async_request_refresh()
