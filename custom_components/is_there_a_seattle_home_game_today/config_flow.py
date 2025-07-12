"""Config flow for Is there a Seattle Home Game Today?"""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import aiohttp

from .const import DOMAIN, API_URL


class WebsiteMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Seattle Home Game Monitor."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate URL
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(API_URL) as response:
                        if response.status == 200:
                            # Create entry
                            return self.async_create_entry(
                                title="Seattle Home Game Monitor",
                                data=user_input,
                            )
                        else:
                            errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", errors=errors, description_placeholders={"api_url": API_URL}
        )
