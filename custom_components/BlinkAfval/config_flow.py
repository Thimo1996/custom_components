import aiohttp
from homeassistant import config_entries
import voluptuous as vol
import requests
from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class MyCustomComponentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Custom Component."""

    VERSION = 1


    def __init__(self):
        """Initialize the config flow."""
        self._data = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the address using the JSON API
            rs = await self.validate_address(user_input["zip_code"], user_input["address_number"])
            if rs == False:
                # Address is not valid, show an error message
                errors["base"] = "Invalid address. Please check your zip code and address number."
            else:
                # Address is valid, proceed to the next step
                return await self.async_step_url()
                
        
        # Define the schema for this step with translation keys
        schema = vol.Schema({
            vol.Required("zip_code"): str,
            vol.Required("address_number"): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

    async def async_step_url(self,id):
        """Handle the URL step."""
        self._data["blinkID"] = id
        self._data["url"] = f"https://www.mijnblink.nl/rest/adressen/{id}/kalender/2024"
        return self.async_create_entry(title="My Integration", data=self._data)

    async def validate_address(self, zip_code:str, address_number):
        """Validate the address using a JSON API."""
        # Make a request to the JSON API to validate the address
        # Replace the URL with your actual JSON API endpoint
        zipcode = zip_code.replace(" ","")
        url = f"https://www.mijnblink.nl/adressen/{zip_code}:{address_number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        data = response.json()
                        return data[0].get("bagid")
                else:
                    return False
    