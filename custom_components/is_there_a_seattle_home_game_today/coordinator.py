"""DataUpdateCoordinator for Seattle Home Game Monitor."""

from typing import Optional

import logging
from datetime import datetime
import aiohttp
import re
from zoneinfo import ZoneInfo
from homeassistant.util import dt as dt_util

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry


from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, API_URL

_LOGGER = logging.getLogger(__name__)


class IsThereASeattleHomeGameTodayCoordinator(DataUpdateCoordinator):
    """Seattle Home Game Monitor coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.entry = entry

    def _extract_time_from_description(self, description: str) -> str | None:
        """Extract time from description text."""
        # Look for patterns like "3:04 PM", "10:30 AM", "7:00PM" etc.
        time_patterns = [
            r"starts\s+at\s+(\d{1,2}:\d{2}\s*[APap][Mm])",  # starts at 3:04 PM
            r"at\s+(\d{1,2}:\d{2}\s*[APap][Mm])",  # at 3:04 PM
            r"\b(\d{1,2}:\d{2}\s*[APap][Mm])\b",  # 3:04 PM or 3:04PM
            r"\b(\d{1,2}:\d{2}\s*[ap]\.m\.)\b",  # 3:04 p.m.
        ]

        for pattern in time_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                # Normalize the time format
                time_str = match.group(1)
                # Remove extra spaces and standardize AM/PM
                time_str = re.sub(r"\s+", " ", time_str).strip()
                time_str = re.sub(r"([ap])\.m\.", r"\1m", time_str, flags=re.IGNORECASE)
                return time_str.upper()

        return None

    def _parse_time_to_datetime(
        self, time_str: str | None, date_str: str
    ) -> datetime | None:
        """Convert time string to datetime object."""
        if not time_str:
            return None

        try:
            # Parse the time
            time_formats = [
                "%I:%M %p",  # 3:04 PM
                "%I:%M%p",  # 3:04PM
            ]

            for fmt in time_formats:
                try:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    seattle_tz = ZoneInfo("America/Los_Angeles")
                    without_tz = datetime.combine(event_date, parsed_time)
                    return without_tz.replace(tzinfo=seattle_tz)
                except ValueError:
                    continue

        except Exception as e:
            _LOGGER.debug(f"Could not parse time {time_str}: {e}")

        return None

    def _process_event(self, event: dict, date_str: str) -> dict:
        """Process a single event to extract all information."""
        description = event.get("description", "")
        event_time = event.get("local_time")

        if not event_time:
            event_time = self._extract_time_from_description(description)

        # Parse venue from description
        venue = None
        venue_patterns = [
            r"at\s+([^.]+?)(?:\.|$)",  # "at Lumen Field."
            r"is\s+at\s+([^.]+?)(?:\.|$)",  # "is at Climate Pledge Arena."
        ]

        for pattern in venue_patterns:
            match = re.search(pattern, description)
            if match:
                venue = match.group(1).strip()
                # Remove time from venue if it got included
                venue = re.sub(
                    r"\.\s*(?:It\s+)?(?:starts\s+at|The\s+game\s+is\s+at)\s+\d{1,2}:\d{2}\s*[APap][Mm].*",
                    "",
                    venue,
                ).strip()
                break

        return {
            "description": description,
            "time": event_time,
            "venue": venue,
            "datetime": (
                self._parse_time_to_datetime(event_time, date_str)
                if event_time
                else None
            ),
        }

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL) as response:
                    if response.status != 200:
                        raise UpdateFailed(
                            f"Error fetching {API_URL}: {response.status}"
                        )

                    data = await response.json()

            # Process events
            date_str = data.get("date", "")
            raw_events = data.get("events", [])
            processed_events = [
                self._process_event(event, date_str) for event in raw_events
            ]

            # Sort events by time if available
            processed_events.sort(key=lambda e: (e["datetime"] is None, e["datetime"]))

            return {
                "date": date_str,
                "events": processed_events,
                "raw_events": raw_events,
                "events_found": data.get("events_found", False),
                "last_poll": dt_util.now(),
                "event_count": len(processed_events),
            }

        except aiohttp.ContentTypeError as err:
            raise UpdateFailed(f"Invalid response format: {err}")
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
