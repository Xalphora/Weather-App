# Extended GTK window and application (CLI readout panel on the main window).

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import CLI_PANEL_PLACEHOLDER, GUI_TITLE_MAIN_WINDOW, LOG_PREFIX_CLI
import weather_cli
from weather_widget import CityPrompt, WeatherApp

if TYPE_CHECKING:
    from gi.repository import Gtk as GtkTypes


class WeatherMainWindow(CityPrompt):
    """CityPrompt plus an extra label for CLI-style output."""

    def __init__(self, application: GtkTypes.Application) -> None:
        super().__init__(application)
        self.set_title(GUI_TITLE_MAIN_WINDOW)
        self.set_default_size(420, 220)

        self._cli_panel = Gtk.Label(
            label=CLI_PANEL_PLACEHOLDER,
            wrap=True,
            xalign=0.0,
            css_classes=["dim-label"],
        )

        child = self.get_child()
        assert isinstance(child, Gtk.Box)
        child.append(Gtk.Separator())
        child.append(self._cli_panel)

    def on_success(self, data: dict, icon_bytes: bytes | None) -> None:
        super().on_success(data, icon_bytes)
        summary = weather_cli.format_summary(data)
        self._cli_panel.set_label(summary)
        print(f"{LOG_PREFIX_CLI}", summary.replace("\n", " | "))

    def on_error(self, message: str) -> None:
        super().on_error(message)
        self._cli_panel.set_label(f"CLI: {message}")


class MainWeatherApp(WeatherApp):
    def do_activate(self) -> None:
        window = WeatherMainWindow(self)
        window.present()


def run_gtk_application(argv: list[str] | None = None) -> int:
    """Start the GTK event loop; blocks until all windows are closed."""
    if argv is None:
        argv = sys.argv
    return MainWeatherApp().run(argv)
