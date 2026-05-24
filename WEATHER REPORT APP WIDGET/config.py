# Shared application constants (names, API endpoints, UI titles, log prefixes).

from __future__ import annotations

APP_NAME = "Weather App"

GUI_TITLE_MAIN_WINDOW = "Weather Widget"
GUI_TITLE_BASE_WINDOW = "Weather"
APPLICATION_ID = "dev.example.weather_widget"

API_URL = "http://api.weatherapi.com/v1/current.json"
REQUEST_TIMEOUT = 15  # seconds
UPDATE_INTERVAL_SEC = 10 * 60

API_KEY_PLACEHOLDER = "YOUR_KEY_HERE"

LOG_PREFIX_WEATHER = "[weather]"
LOG_PREFIX_CLI = "[cli]"
LOG_PREFIX_MAIN = "[main]"

CLI_PANEL_PLACEHOLDER = "CLI readout appears here after a successful fetch."
STATUS_PLACEHOLDER = "Enter a city, then press Enter or Refresh."
ENTRY_PLACEHOLDER = "City name"
REFRESH_BUTTON_LABEL = "Refresh"
ALREADY_LOADING_MESSAGE = "Already loading…"
