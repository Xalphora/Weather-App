# Shared API key — main.py calls configure(); widget/CLI/API call get_api_key().

from __future__ import annotations

import os
from typing import Optional

from config import API_KEY_PLACEHOLDER

_configured_key: Optional[str] = None


def configure(api_key: str) -> None:
    """Called once from main.py at startup."""
    global _configured_key
    key = api_key.strip()
    if not key or key == API_KEY_PLACEHOLDER:
        raise RuntimeError(
            f"Set your WeatherAPI key in main.py ({API_KEY_PLACEHOLDER!r} → your real key).\n"
            "  https://www.weatherapi.com/"
        )
    _configured_key = key
    os.environ["WEATHER_API_KEY"] = key


def get_api_key() -> str:
    if _configured_key:
        return _configured_key
    key = os.environ.get("WEATHER_API_KEY", "").strip()
    if key and key != API_KEY_PLACEHOLDER:
        return key
    raise RuntimeError(
        "No API key configured. Put your key in main.py or export WEATHER_API_KEY."
    )
