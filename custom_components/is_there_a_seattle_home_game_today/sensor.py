"""Sensor platform for Is There a Seattle Home Game Today?"""

from datetime import datetime
from homeassistant.components.sensor import SensorEntity
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
    """Set up Seattle Home Game sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        LastPollSensor(coordinator),
        EventDateSensor(coordinator),
        EventCountSensor(coordinator),
    ]

    for i in range(5):
        sensors.append(EventDetailSensor(coordinator, i))

    async_add_entities(sensors)


class LastPollSensor(CoordinatorEntity, SensorEntity):
    """Last poll time sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Last Poll Time"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_last_poll"
        self._attr_device_class = "timestamp"
        self._attr_icon = "mdi:clock-check"

    @property
    def native_value(self):
        """Return the last poll time."""
        last_poll = self.coordinator.data.get("last_poll")
        return last_poll if last_poll else None


class EventDateSensor(CoordinatorEntity, SensorEntity):
    """Event date sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Event Date"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_event_date"
        self._attr_icon = "mdi:calendar"

    @property
    def native_value(self):
        """Return the event date."""
        return self.coordinator.data.get("date")


class EventCountSensor(CoordinatorEntity, SensorEntity):
    """Event count sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Event Count"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_event_count"
        self._attr_icon = "mdi:counter"

    @property
    def native_value(self):
        """Return the number of events."""
        return self.coordinator.data.get("event_count", 0)


class EventDetailSensor(CoordinatorEntity, SensorEntity):
    """Individual event detail sensor."""

    def __init__(self, coordinator, index):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._index = index
        self._attr_name = f"Event {index + 1}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_event_{index}"
        self._attr_icon = "mdi:calendar-text"

    @property
    def native_value(self):
        """Return the event name."""
        events = self.coordinator.data.get("events", [])
        if self._index < len(events):
            return events[self._index].get("name", "Event")
        return "No event"

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        events = self.coordinator.data.get("events", [])
        if self._index < len(events):
            event = events[self._index]
            attrs = {
                "description": event.get("description"),
                "time": event.get("time"),
                "venue": event.get("venue"),
            }

            # Add datetime if available
            if event.get("datetime"):
                attrs["datetime"] = event["datetime"].isoformat()

            # Add time status
            if event.get("time"):
                attrs["has_time"] = True
            else:
                attrs["has_time"] = False

            return attrs
        return {}

    @property
    def available(self):
        """Return if entity is available."""
        events = self.coordinator.data.get("events", [])
        return self._index < len(events)
