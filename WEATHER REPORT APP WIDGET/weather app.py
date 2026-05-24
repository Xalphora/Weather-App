# Optional: run in terminal only —  python3 "weather app.py"
# Uses the same API key as main.py (reads WEATHER_API_KEY from main.py if needed).

from __future__ import annotations

import weather_cli


def _ensure_configured() -> None:
    from weather_config import configure, get_api_key

    try:
        get_api_key()
    except RuntimeError:
        from main import WEATHER_API_KEY

        configure(WEATHER_API_KEY)


def main() -> int:
    try:
        _ensure_configured()
    except RuntimeError as exc:
        print("Error:", exc)
        return 1

    city = input("Enter city name: ").strip()
    try:
        data = weather_cli.fetch_current(city)
    except (RuntimeError, ValueError) as exc:
        print("Error:", exc)
        return 1
    weather_cli.print_summary(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
