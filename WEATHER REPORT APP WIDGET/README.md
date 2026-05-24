# Weather Widget (GTK4)

GTK4 weather widget + CLI readout, one entry point.

## Project layout

```
main.py              ← paste API key here; run this
weather_config.py    ← shared key (main.py / env)
weather_widget.py    ← GTK fetch + CityPrompt (extend UI here)
weather_cli.py       ← CLI fetch + text formatting
weather app.py       ← optional terminal-only script (same key)
```

## Install (Ubuntu)

```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-4.0
pip install requests
```

## API key

Open **`main.py`** and replace `YOUR_KEY_HERE` with your key from [weatherapi.com](https://www.weatherapi.com/):

```python
WEATHER_API_KEY = "abc123..."
```

Alternatively, export `WEATHER_API_KEY` in the shell (used if you run `weather_widget.py` directly without editing `main.py`).

## Run

```bash
cd "/home/reece/Desktop/WEATHER REPORT APP WIDGET"
python3 main.py
```

This opens the GTK window (city entry, Refresh) and a **CLI readout** panel below that mirrors the old `weather app.py` output on each successful fetch.

Terminal-only (same key from `main.py` if configured):

```bash
python3 "weather app.py"
```

## Where to plug UI code

| Goal | Location |
|------|----------|
| Combined app shell | **`main.py`** → `WeatherMainWindow` |
| Widget UI | **`weather_widget.py`** → `CityPrompt.on_success` / `on_error` |
| Network / threading | **`weather_widget.py`** → `fetch_weather()` |
| CLI text / extra prints | **`weather_cli.py`** → `format_summary()` |

Optional periodic refresh (not auto-started):

```python
window.start_periodic_refresh()  # 10 minutes
```
