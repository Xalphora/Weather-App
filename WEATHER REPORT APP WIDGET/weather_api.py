# WeatherAPI HTTP client — blocking requests shared by GTK worker and CLI.

from __future__ import annotations

import json
import logging
from typing import Any, Optional

import requests

from config import API_URL, LOG_PREFIX_WEATHER, REQUEST_TIMEOUT
from weather_config import get_api_key

_log = logging.getLogger("weather_app")


def http_error_message(resp: requests.Response) -> str:
    """Short error string from HTTP status and API/response body (GTK fetch path)."""
    try:
        body = resp.json()
        err = body.get("error")
        if isinstance(err, dict) and err.get("message"):
            return f"HTTP {resp.status_code}: {err['message']}"
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    snippet = (resp.text or "").strip().replace("\n", " ")
    if len(snippet) > 200:
        snippet = snippet[:200] + "..."
    return f"HTTP {resp.status_code}: {snippet or resp.reason}"


def cli_http_error(resp: requests.Response) -> RuntimeError:
    """Raise RuntimeError for failed CLI responses (matches legacy weather_cli.py)."""
    try:
        err = resp.json().get("error", {})
        if isinstance(err, dict) and err.get("message"):
            return RuntimeError(f"HTTP {resp.status_code}: {err['message']}")
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    return RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")


def _validate_response(data: Any, *, require_location: bool) -> None:
    if not isinstance(data, dict) or "current" not in data:
        raise RuntimeError("Unexpected API response format.")
    if require_location and "location" not in data:
        raise RuntimeError("Unexpected API response format (missing location/current).")


def _log_error(msg: str, *, emit_logs: bool) -> None:
    if emit_logs:
        print(f"{LOG_PREFIX_WEATHER} ERROR: {msg}")
    _log.error(msg)


def fetch_current(
    city: str,
    *,
    require_location: bool = False,
    emit_logs: bool = True,
) -> dict[str, Any]:
    """
    Blocking weather fetch. GTK uses require_location=True and emit_logs=True.
    CLI uses require_location=False and emit_logs=False (it prints [cli] itself).
    """
    city_clean = city.strip()
    if not city_clean:
        raise ValueError("City name cannot be empty.")

    params = {"key": get_api_key(), "q": city_clean, "aqi": "no"}
    if emit_logs:
        print(f"{LOG_PREFIX_WEATHER} GET {API_URL} q={city_clean!r}")
    _log.info("GET %s q=%r", API_URL, city_clean)

    try:
        resp = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
    except requests.Timeout as exc:
        msg = f"Request timed out after {REQUEST_TIMEOUT} seconds."
        _log_error(msg, emit_logs=emit_logs)
        raise RuntimeError(msg) from exc
    except requests.RequestException as exc:
        msg = f"Network error: {exc}"
        _log_error(msg, emit_logs=emit_logs)
        raise RuntimeError(msg) from exc

    if not resp.ok:
        if require_location:
            msg = http_error_message(resp)
            _log_error(msg, emit_logs=emit_logs)
            raise RuntimeError(msg)
        raise cli_http_error(resp)

    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        msg = f"Could not parse API response as JSON: {exc}"
        _log_error(msg, emit_logs=emit_logs)
        raise RuntimeError(msg) from exc

    try:
        _validate_response(data, require_location=require_location)
    except RuntimeError as exc:
        _log_error(str(exc), emit_logs=emit_logs)
        raise

    return data


def download_icon(data: dict[str, Any]) -> Optional[bytes]:
    """Fetch condition icon bytes; returns None on failure (widget still works)."""
    icon_path = data.get("current", {}).get("condition", {}).get("icon")
    if not icon_path:
        return None

    icon_url = str(icon_path)
    if icon_url.startswith("//"):
        icon_url = "https:" + icon_url
    elif icon_url.startswith("http://"):
        icon_url = "https://" + icon_url[len("http://") :]

    print(f"{LOG_PREFIX_WEATHER} GET icon {icon_url}")
    _log.info("Downloading icon %s", icon_url)
    try:
        icon_resp = requests.get(icon_url, timeout=REQUEST_TIMEOUT)
        icon_resp.raise_for_status()
        return icon_resp.content
    except requests.Timeout:
        print(f"{LOG_PREFIX_WEATHER} WARN: icon request timed out after {REQUEST_TIMEOUT}s")
        _log.warning("Icon download timed out")
    except requests.RequestException as exc:
        print(f"{LOG_PREFIX_WEATHER} WARN: icon download failed: {exc}")
        _log.warning("Icon download failed: %s", exc)
    return None
