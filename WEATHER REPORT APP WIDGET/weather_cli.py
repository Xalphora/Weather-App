# Terminal-style weather text — no GTK here.
# app_gui.py uses format_summary() for the extra panel; weather app.py uses fetch_current().

from __future__ import annotations

from typing import Any

from config import API_URL, LOG_PREFIX_CLI, REQUEST_TIMEOUT
from weather_api import fetch_current as _fetch_current

# Re-export for callers that import these names (behavior unchanged).
__all__ = ["API_URL", "REQUEST_TIMEOUT", "fetch_current", "format_summary", "print_summary"]


def fetch_current(city: str) -> dict[str, Any]:
    """Blocking HTTP fetch (runs on main thread — fine for terminal script only)."""
    city_clean = city.strip()
    print(f"{LOG_PREFIX_CLI} GET {API_URL} q={city_clean!r}")
    return _fetch_current(city, require_location=False, emit_logs=False)


def format_summary(data: dict[str, Any]) -> str:
    """Turn API JSON into human-readable text for labels or print()."""
    name = data["location"]["name"]
    temp_c = data["current"]["temp_c"]
    cond = data["current"]["condition"]["text"]
    icon = data["current"]["condition"]["icon"]
    if str(icon).startswith("//"):
        icon = "https:" + icon
    return f"{name}: {temp_c}°C, {cond}\nIcon: {icon}"


def print_summary(data: dict[str, Any]) -> None:
    print(format_summary(data))
