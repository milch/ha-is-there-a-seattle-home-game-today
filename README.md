# `Is there a Seattle Home Game Today?` for Home Assistant

<img src="https://raw.githubusercontent.com/milch/ha-is-there-a-seattle-home-game-today/main/logo.png" alt="Is There a Seattle Home Game Today?" width="200">

Integrate Home Assistant with [isthereaseattlehomegametoday.com](https://isthereaseattlehomegametoday.com) to monitor Seattle home game events. Uses the API endpoint to regularly fetch new event data. `Is There a Seattle Home Game Today?` is generally updated about once a day.

## 📋 Entities Created

### Binary Sensor

- **`binary_sensor.seattle_home_game_today`** - On when events are found
  - **Attributes:**
    - `event_count` - Total number of events.
    - `summary` - Natural language summary of events happening today. Generally includes the number of events, venues, and times, but not the actual event descriptions.
    - `events` - List of raw event data. Fields vary by event type.

### Sensors

- **`sensor.event_date`** - Date of events (YYYY-MM-DD format). Corresponds to the date that the API refreshed the data. The other sensors are all "valid" as of this date.
- **`sensor.event_count`** - Number of events today.
- **`sensor.event_1`** through **`sensor.event_5`** - Individual event details
  - **Attributes:** `time`, `venue`, `description`, `has_time`
- **`sensor.last_poll_time`** - Timestamp of last data update, i.e. when the API was last polled.

### Switch

- **`switch.manual_refresh`** - Trigger immediate data update

## 🚀 Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots menu in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/milch/ha-is-there-a-seattle-home-game-today`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "Is There a Seattle Home Game Today?"
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from GitHub
2. Extract the `custom_components/website_monitor` folder
3. Copy it to your Home Assistant `custom_components` directory
4. Restart Home Assistant

## ⚙️ Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"Is There a Seattle Home Game Today?"**
4. Click to add - no configuration needed!

## 🤖 Automation Examples

### Morning Traffic Warning

```yaml
automation:
  - alias: "Game Day Traffic Alert"
    trigger:
      - platform: time
        at: "06:30:00"
    condition:
      - condition: state
        entity_id: binary_sensor.seattle_home_game_today
        state: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Game Day Traffic Alert"
          message: >
            {{ state_attr('binary_sensor.seattle_home_game_today', 'summary') }}
            Plan your commute accordingly!
          data:
            tag: "game-day-traffic"
            group: "traffic"
```

### Detailed Event Notifications

```yaml
automation:
  - alias: "Detailed Game Schedule"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.seattle_home_game_today
        state: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Today's Seattle Events"
          message: >
            {% set events = state_attr('binary_sensor.seattle_home_game_today', 'event_summary') %}
            {% for event in events %}
            📍 {{ event }}
            {% endfor %}
```

## 🧪 Development & Testing

### Local Testing with Docker

1. Clone the repository
1. Create a `config` directory
1. Run: `docker-compose up`
1. Access Home Assistant at `http://localhost:8123`
1. Complete onboarding and add the integration

## 🛠️ Troubleshooting

### No Data or Old Data

- Check if the API is accessible: <https://isthereaseattlehomegametoday.com/todays_events.json>
- Check `sensor.last_poll_time` to see when data was last fetched
- Use the manual refresh switch to force an update
- Review Home Assistant logs for connection errors

### Time Zone Issues

- The integration assumes events are in Pacific Time (Seattle)
- Ensure your Home Assistant instance has the correct timezone configured
- Event times are converted to your local timezone for display

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🙏 Credits

This project does not include any data on its own. All event data is provided by [isthereaseattlehomegametoday.com](https://isthereaseattlehomegametoday.com).
