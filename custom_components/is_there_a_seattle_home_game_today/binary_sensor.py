"""Binary sensor platform for Is There a Seattle Home Game Today?"""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from collections import defaultdict

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Seattle Home Game binary sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([SeattleHomeGameBinarySensor(coordinator)])


class SeattleHomeGameBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Seattle home game binary sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Is There a Seattle Home Game Today?"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_home_game_today"

    @property
    def is_on(self):
        """Return true if there are events today."""
        return self.coordinator.data.get("events_found", False)

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:stadium" if self.is_on else "mdi:stadium-outline"

    def _format_time_and_venue(self, time, venue):
        """Format time and venue information."""
        if time and venue:
            return f"at {time} at {venue}"
        elif time:
            return f"at {time}"
        elif venue:
            return f"at {venue}"
        else:
            return "with no time or venue listed"

    def _group_events(self, events):
        """Group events by venue and time for more natural summaries."""
        # Group by venue
        by_venue = defaultdict(list)
        no_venue = []

        for event in events:
            venue = event.get("venue")
            if venue:
                by_venue[venue].append(event)
            else:
                no_venue.append(event)

        # Further group by time within each venue
        venue_time_groups = {}
        for venue, venue_events in by_venue.items():
            time_groups = defaultdict(list)
            for event in venue_events:
                time = event.get("time", "No time")
                time_groups[time].append(event)
            venue_time_groups[venue] = time_groups

        return venue_time_groups, no_venue

    def _generate_summary(self, events):
        """Generate a human-readable summary of events."""
        if not events:
            return "There are no events today"

        event_count = len(events)

        # Single event case
        if event_count == 1:
            event = events[0]
            time = event.get("time")
            venue = event.get("venue")

            if time and venue:
                return f"There is one event today at {venue}, starting at {time}"
            elif time:
                return f"There is one event today, starting at {time}"
            elif venue:
                return f"There is one event today at {venue}"
            else:
                return "There is one event today"

        # Multiple events
        venue_time_groups, no_venue = self._group_events(events)

        # Check if all events are at the same venue
        if len(venue_time_groups) == 1 and not no_venue:
            venue = list(venue_time_groups.keys())[0]
            time_groups = venue_time_groups[venue]

            # All at same venue
            if len(time_groups) == 1:
                time = list(time_groups.keys())[0]
                if time != "No time":
                    return f"There are {event_count} events today at {venue}, all starting at {time}"
                else:
                    return f"There are {event_count} events today at {venue}"
            else:
                # Same venue, different times
                times_with_events = [
                    (t, len(evts)) for t, evts in time_groups.items() if t != "No time"
                ]
                times_with_events.sort(
                    key=lambda x: events[
                        next(i for i, e in enumerate(events) if e.get("time") == x[0])
                    ].get("datetime")
                )

                if times_with_events:
                    time_parts = []
                    for time, count in times_with_events:
                        if count > 1:
                            time_parts.append(f"{count} at {time}")
                        else:
                            time_parts.append(time)

                    if len(time_parts) == 1:
                        return f"There are {event_count} events today at {venue}, starting at {time_parts[0]}"
                    elif len(time_parts) == 2:
                        return f"There are {event_count} events today at {venue}, starting at {time_parts[0]} and {time_parts[1]}"
                    else:
                        times_str = (
                            ", ".join(time_parts[:-1]) + f", and {time_parts[-1]}"
                        )
                        return f"There are {event_count} events today at {venue}, starting at {times_str}"
                else:
                    return f"There are {event_count} events today at {venue}"

        # Check if all events are at the same time
        all_times = []
        for venue_events in venue_time_groups.values():
            all_times.extend([t for t in venue_events.keys() if t != "No time"])
        all_times.extend([e.get("time") for e in no_venue if e.get("time")])

        unique_times = list(set(all_times))
        if (
            len(unique_times) == 1
            and unique_times[0]
            and not any(e for e in events if not e.get("time"))
        ):
            # All at same time, different venues
            time = unique_times[0]
            venues = list(venue_time_groups.keys())

            if len(venues) == 2 and not no_venue:
                return f"There are {event_count} events today at {time}, at {venues[0]} and {venues[1]}"
            elif len(venues) == 1 and no_venue:
                return f"There are {event_count} events today at {time} ({len(venue_time_groups[venues[0]])} at {venues[0]}, {len(no_venue)} with no venue listed)"
            else:
                return f"There are {event_count} events today, all starting at {time}"

        # Complex case - build a comprehensive summary
        parts = []

        # Group venues by number of events for better readability
        venue_counts = [
            (v, sum(len(events) for events in tg.values()))
            for v, tg in venue_time_groups.items()
        ]
        venue_counts.sort(key=lambda x: x[1], reverse=True)

        # If there are 2 or fewer venues, we can be more detailed
        if len(venue_counts) <= 2 and not no_venue:
            for venue, count in venue_counts:
                time_groups = venue_time_groups[venue]
                times_with_events = [
                    (t, len(evts)) for t, evts in time_groups.items() if t != "No time"
                ]

                if times_with_events:
                    if len(times_with_events) == 1 and times_with_events[0][1] == 1:
                        parts.append(f"{times_with_events[0][0]} at {venue}")
                    else:
                        times_str = " and ".join([t[0] for t in times_with_events])
                        if count == 1:
                            parts.append(f"{venue} at {times_str}")
                        else:
                            parts.append(f"{count} at {venue} ({times_str})")
                else:
                    parts.append(f"{count} at {venue}")

            if len(parts) == 1:
                return f"There are {event_count} events today: {parts[0]}"
            else:
                return f"There are {event_count} events today: {' and '.join(parts)}"

        # For many venues or complex scenarios, provide a simpler summary
        venues_mentioned = len(venue_counts)
        if venues_mentioned == 1:
            venue_str = venue_counts[0][0]
        elif venues_mentioned == 2:
            venue_str = f"{venue_counts[0][0]} and {venue_counts[1][0]}"
        else:
            venue_str = f"{venues_mentioned} different venues"

        # Count events with times
        events_with_time = sum(1 for e in events if e.get("time"))

        if events_with_time == event_count:
            if len(unique_times) <= 2:
                times_str = " and ".join(unique_times)
                return f"There are {event_count} events today at {venue_str}, starting at {times_str}"
            else:
                return f"There are {event_count} events today at {venue_str} at various times"
        elif events_with_time > 0:
            return f"There are {event_count} events today at {venue_str} ({events_with_time} with times listed)"
        else:
            return f"There are {event_count} events today at {venue_str}"

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        events = self.coordinator.data.get("events", [])
        return {
            "event_count": len(events),
            "events": events,
            "summary": self._generate_summary(events),
        }
