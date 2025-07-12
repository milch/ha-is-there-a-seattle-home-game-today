"""Switch platform for Is There a Seattle Home Game Today?"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Website Monitor switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([RefreshSwitch(coordinator)])


class RefreshSwitch(SwitchEntity):
    """Switch to manually refresh data."""

    def __init__(self, coordinator):
        """Initialize the switch."""
        self.coordinator = coordinator
        self._attr_name = "Manual Refresh"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_refresh"
        self._attr_icon = "mdi:refresh"
        self._is_on = False

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on and refresh data."""
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_refresh()
        self._is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        self.async_write_ha_state()
