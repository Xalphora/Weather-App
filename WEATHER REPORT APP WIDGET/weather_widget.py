#!/usr/bin/env python3
# GTK4 weather widget — UI + async fetch orchestration.
# Customize UI: override on_success / on_error, or subclass in app_gui.py.

from __future__ import annotations

import logging
import sys
import threading
from typing import Any, Callable, Optional

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402

from config import (
    ALREADY_LOADING_MESSAGE,
    APPLICATION_ID,
    ENTRY_PLACEHOLDER,
    GUI_TITLE_BASE_WINDOW,
    LOG_PREFIX_WEATHER,
    REFRESH_BUTTON_LABEL,
    STATUS_PLACEHOLDER,
    UPDATE_INTERVAL_SEC,
)
from weather_api import download_icon, fetch_current
from weather_config import get_api_key

_log = logging.getLogger("weather_app")


def _schedule_main(callback: Callable[..., None], *args: Any) -> None:
    def _run() -> bool:
        callback(*args)
        return False

    GLib.idle_add(_run)


def fetch_weather(
    city: str,
    on_success: Callable[[dict, Optional[bytes]], None],
    on_error: Callable[[str], None],
) -> None:
    """Start a background fetch; invoke callbacks on the GTK main thread."""

    def worker() -> None:
        city_clean = city.strip()
        if not city_clean:
            _schedule_main(on_error, "City name cannot be empty.")
            return

        try:
            get_api_key()
        except RuntimeError as exc:
            msg = str(exc)
            print(f"{LOG_PREFIX_WEATHER} ERROR: {msg}")
            _log.error(msg)
            _schedule_main(on_error, msg)
            return

        try:
            data = fetch_current(city, require_location=True, emit_logs=True)
        except ValueError as exc:
            _schedule_main(on_error, str(exc))
            return
        except RuntimeError as exc:
            _schedule_main(on_error, str(exc))
            return

        icon_bytes = download_icon(data)
        print(
            f"{LOG_PREFIX_WEATHER} OK {city_clean!r}"
            + (f", icon={len(icon_bytes)} bytes" if icon_bytes else ", no icon")
        )
        _log.info("Weather OK for %r", city_clean)
        _schedule_main(on_success, data, icon_bytes)

    threading.Thread(target=worker, name="weather-fetch", daemon=True).start()


class CityPrompt(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(
            application=application,
            title=GUI_TITLE_BASE_WINDOW,
            default_width=380,
            default_height=140,
        )

        self._busy = False
        self._periodic_source_id: Optional[int] = None

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12,
        )

        self._entry = Gtk.Entry(placeholder_text=ENTRY_PLACEHOLDER)
        self._entry.connect("activate", self._on_activate)

        refresh = Gtk.Button(label=REFRESH_BUTTON_LABEL)
        refresh.connect("clicked", self._on_refresh_clicked)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.append(self._entry)
        row.append(refresh)

        self._status = Gtk.Label(
            label=STATUS_PLACEHOLDER,
            wrap=True,
            xalign=0.0,
        )

        root.append(row)
        root.append(self._status)
        self.set_child(root)

    # --- Event handlers ---

    def _on_activate(self, _entry: Gtk.Entry) -> None:
        self.refresh()

    def _on_refresh_clicked(self, _button: Gtk.Button) -> None:
        self.refresh()

    def _on_periodic_tick(self) -> bool:
        self.refresh()
        return True

    # --- Public API ---

    def refresh(self) -> None:
        if self._busy:
            self._set_status(ALREADY_LOADING_MESSAGE)
            return

        city = self._entry.get_text()
        self._busy = True
        label = city.strip() or "…"
        self._set_status(f"Loading {label}…")

        fetch_weather(
            city,
            on_success=self._dispatch_success,
            on_error=self._dispatch_error,
        )

    def on_success(self, data: dict, icon_bytes: Optional[bytes]) -> None:
        location = data.get("location", {})
        current = data.get("current", {})
        name = location.get("name", "?")
        temp_c = current.get("temp_c", "?")
        condition = current.get("condition", {}).get("text", "?")
        icon_hint = f", icon {len(icon_bytes)} bytes" if icon_bytes else ""
        self._set_status(f"{name}: {temp_c}°C — {condition}{icon_hint}")
        _ = icon_bytes

    def on_error(self, message: str) -> None:
        self._set_status(f"Error: {message}")

    def start_periodic_refresh(self, interval_sec: int = UPDATE_INTERVAL_SEC) -> None:
        self.stop_periodic_refresh()
        self._periodic_source_id = GLib.timeout_add_seconds(
            interval_sec,
            self._on_periodic_tick,
        )
        print(f"{LOG_PREFIX_WEATHER} periodic refresh every {interval_sec}s")

    def stop_periodic_refresh(self) -> None:
        if self._periodic_source_id is not None:
            GLib.source_remove(self._periodic_source_id)
            self._periodic_source_id = None

    # --- Internal dispatch ---

    def _dispatch_success(self, data: dict, icon_bytes: Optional[bytes]) -> None:
        self._busy = False
        self.on_success(data, icon_bytes)

    def _dispatch_error(self, message: str) -> None:
        self._busy = False
        self.on_error(message)

    def _set_status(self, text: str) -> None:
        self._status.set_label(text)


class WeatherApp(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APPLICATION_ID)

    def do_activate(self) -> None:
        window = CityPrompt(self)
        window.present()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    try:
        get_api_key()
    except RuntimeError as exc:
        print(f"{LOG_PREFIX_WEATHER} FATAL: {exc}", file=sys.stderr)
        print(
            f"{LOG_PREFIX_WEATHER} Tip: run python3 main.py and set WEATHER_API_KEY in main.py",
            file=sys.stderr,
        )
        return 1

    return WeatherApp().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
