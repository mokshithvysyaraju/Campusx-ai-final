"""
weather.py — Mock weather feed for CAMPUSX AI

Stands in for a real weather-API integration (e.g. OpenWeather). There
is no network call here — a 7-day outlook is generated from a seed so
it stays stable within a session, and each condition maps to an
"energy multiplier" that nudges the campus's predicted energy draw,
since hotter/sunnier days push cooling load up and cooler/rainy days
ease it back down.
"""

import random
from datetime import date, timedelta

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

CONDITIONS = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Hot & Humid"]

_BASE_TEMP = {"Sunny": 31, "Partly Cloudy": 29, "Cloudy": 27, "Rainy": 25, "Hot & Humid": 34}
_BASE_HUMIDITY = {"Sunny": 55, "Partly Cloudy": 60, "Cloudy": 68, "Rainy": 85, "Hot & Humid": 78}
_ICONS = {"Sunny": "☀️", "Partly Cloudy": "⛅", "Cloudy": "☁️", "Rainy": "🌧️", "Hot & Humid": "🥵"}

# How much each condition nudges expected energy draw vs. baseline
# (1.0 = no change). Hot/humid/sunny days raise AC load; rainy/cooler
# days ease it slightly.
_CONDITION_MULTIPLIER = {
    "Sunny": 1.08,
    "Partly Cloudy": 1.02,
    "Cloudy": 0.97,
    "Rainy": 0.90,
    "Hot & Humid": 1.18,
}


def get_forecast(seed: str = "campusx-week") -> list[dict]:
    """
    Return a 7-entry mock forecast starting today: [{day, date,
    condition, icon, temp_c, humidity}, ...]. Deterministic per seed
    so it's stable within a session — pass a new seed (e.g. including
    a refresh counter) to simulate a new forecast pull.
    """
    rng = random.Random(seed)
    today = date.today()
    forecast = []
    for i in range(7):
        d = today + timedelta(days=i)
        condition = rng.choice(CONDITIONS)
        temp = round(_BASE_TEMP[condition] + rng.uniform(-1.5, 1.5), 1)
        humidity = round(_BASE_HUMIDITY[condition] + rng.uniform(-5, 5))
        forecast.append({
            "day": DAY_NAMES[d.weekday()],
            "date": d.strftime("%d %b"),
            "condition": condition,
            "icon": _ICONS[condition],
            "temp_c": temp,
            "humidity": max(30, min(95, humidity)),
        })
    return forecast


def energy_multiplier(condition: str, temp_c: float) -> float:
    """
    Multiplier applied to a predicted energy value to account for
    weather (1.0 = no change). Combines a per-condition base factor
    with an extra bump for unusually hot days.
    """
    base = _CONDITION_MULTIPLIER.get(condition, 1.0)
    heat_bump = max(0.0, (temp_c - 30)) * 0.01
    return round(base + heat_bump, 3)


if __name__ == "__main__":
    for entry in get_forecast():
        mult = energy_multiplier(entry["condition"], entry["temp_c"])
        print(entry, "-> energy x", mult)
