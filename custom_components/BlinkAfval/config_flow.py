from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class MyCustomComponentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Custom Component."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="My Custom Component", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("url"): str})
        )
