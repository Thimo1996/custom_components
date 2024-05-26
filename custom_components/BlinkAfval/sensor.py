import aiohttp
import logging
from datetime import timedelta, datetime
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

                results = {}
                current_date = datetime.now().date()
                for item in data:
                    afvalstroom_id = item.get("afvalstroom_id")
                    ophaaldatum_str = item.get("ophaaldatum")
                    if afvalstroom_id in [4, 77, 81]:
                        ophaaldatum = datetime.strptime(ophaaldatum_str, "%Y-%m-%d").date()
                        if ophaaldatum >= current_date:
                            if afvalstroom_id not in results or ophaaldatum < results[afvalstroom_id]["ophaaldatum"]:
                                results[afvalstroom_id] = item
                
                closest_results = {k: v["item"] for k, v in results.items()}
                _LOGGER.debug(f"Closest results: {closest_results}")
                return closest_results
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

    sensors = [
        MyCustomSensor(coordinator, 4, "groen"),
        MyCustomSensor(coordinator, 77, "GFT/groenbak"),
        MyCustomSensor(coordinator, 81, "Restafval"),
    ]
    async_add_entities(sensors, True)
    _LOGGER.debug("Entities added")


class MyCustomSensor(SensorEntity):
    def __init__(self, coordinator, afvalstroom_id, name):
        super().__init__()
        self.coordinator = coordinator
        self.afvalstroom_id = afvalstroom_id
        self._attr_name = name
        self._attr_native_value = None
        self._attr_device_class = 'date'  

    @property
    def native_value(self):
        _LOGGER.debug(f"Getting native_value for ID {self.afvalstroom_id}: {self.coordinator.data}")
        date_str = self.coordinator.data.get(self.afvalstroom_id, {}).get("ophaaldatum") if self.coordinator.data else None
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        return None

    @property
    def available(self):
        _LOGGER.debug(f"Checking availability for ID {self.afvalstroom_id}: {self.coordinator.last_update_success}")
        return self.coordinator.last_update_success

    async def async_update(self):
        _LOGGER.debug(f"Requesting refresh for ID {self.afvalstroom_id}")
        await self.coordinator.async_request_refresh()
