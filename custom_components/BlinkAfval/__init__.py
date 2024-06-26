import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
DOMAIN = "hello_state"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    _LOGGER.info("Setting up My Custom Component")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Setting up My Custom Component from Config Entry")
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Unloading My Custom Component Config Entry")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
