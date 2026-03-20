"""Button platform for Is There a Seattle Home Game Today?"""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Seattle Home Game refresh button."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RefreshButton(coordinator)])


class RefreshButton(CoordinatorEntity, ButtonEntity):
    """Button to manually refresh data."""

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "Manual Refresh"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_refresh"
        self._attr_icon = "mdi:refresh"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": "Seattle Home Game Monitor",
            "manufacturer": "isthereaseattlehomegametoday.com",
            "entry_type": "service",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_refresh()
