#!/usr/bin/env python3
# Run this file:  python3 main.py
# Starts the GTK window and loads your API key for both widget + terminal CLI.

from __future__ import annotations

import logging
import sys

# --- Paste your WeatherAPI key here (shared by widget + terminal CLI) ---
WEATHER_API_KEY = "YOUER_WEATHER_API_KEY_HERE"
# -----------------------------------------------------------------------


def run() -> int:
    from weather_config import configure
    from app_gui import run_gtk_application

    try:
        configure(WEATHER_API_KEY)
    except RuntimeError as exc:
        from config import LOG_PREFIX_MAIN

        print(f"{LOG_PREFIX_MAIN} FATAL: {exc}", file=sys.stderr)
        return 1

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    return run_gtk_application(sys.argv)


if __name__ == "__main__":
    raise SystemExit(run())
