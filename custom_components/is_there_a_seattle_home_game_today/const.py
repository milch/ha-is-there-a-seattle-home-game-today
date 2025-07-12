"""Constants for Is There a Seattle Home Game Today?"""

from datetime import timedelta

DOMAIN = "seattle_home_game"
DEFAULT_NAME = "Is There a Seattle Home Game Today?"
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

API_URL = "https://isthereaseattlehomegametoday.com/todays_events.json"

ATTR_EVENTS = "events"
ATTR_DATE = "date"
ATTR_EVENTS_FOUND = "events_found"
ATTR_LAST_POLL = "last_poll"
