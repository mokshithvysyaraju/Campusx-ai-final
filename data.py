"""
data.py — Simulated campus data generator

Generates fake but realistic occupancy / temperature / energy / water
readings for a fixed set of campus locations, and can "advance time"
so the dashboard looks dynamic.
"""

import random
import pandas as pd

LOCATIONS = ["Block A", "Block B", "Library", "Canteen", "Hostel"]

# Real-world anchor point: Vignan's Institute of Information Technology,
# Duvvada, Visakhapatnam. Individual buildings are offset slightly around
# this point since exact per-building coordinates aren't published —
# swap these for surveyed coordinates when real GPS tagging is available.
CAMPUS_NAME = "Vignan's Institute Of Information Technology"
CAMPUS_CENTER = (17.711528, 83.165427)

COORDINATES = {
    "Block A":  (17.710473, 83.165838),
    "Block B":  (17.712183, 83.166195),
    "Library":  (17.710905, 83.165586),
    "Canteen":  (17.711238, 83.165314),
    "Hostel":   (17.712843, 83.164204),
}

# Baseline "normal" ranges per location (used to generate realistic data
# and later reused by detector.py to define what counts as an anomaly)
BASELINES = {
    "Block A":  {"occupancy": (30, 70), "temperature": (23, 27), "energy": (40, 70), "water": (10, 30)},
    "Block B":  {"occupancy": (30, 70), "temperature": (23, 27), "energy": (40, 70), "water": (10, 30)},
    "Library":  {"occupancy": (40, 90), "temperature": (23, 27), "energy": (40, 70), "water": (10, 30)},
    "Canteen":  {"occupancy": (20, 95), "temperature": (24, 29), "energy": (50, 90), "water": (30, 60)},
    "Hostel":   {"occupancy": (50, 95), "temperature": (23, 28), "energy": (60, 100), "water": (40, 80)},
}


# Weekend behavior multiplier applied to occupancy/energy/water on
# Sat/Sun, relative to weekday levels (temperature is weather-driven,
# not weekday/weekend-driven, so it's left out of this table).
# Academic buildings empty out on weekends; the Hostel stays full or
# even ticks up slightly since residents don't leave campus.
WEEKEND_FACTORS = {
    "Block A":  0.30,
    "Block B":  0.30,
    "Library":  0.55,
    "Canteen":  0.65,
    "Hostel":   1.05,
}

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _random_reading(location: str) -> dict:
    """Generate one random-but-plausible reading for a location."""
    b = BASELINES[location]
    return {
        "location": location,
        "occupancy": round(random.uniform(*b["occupancy"]), 1),
        "temperature": round(random.uniform(*b["temperature"]), 1),
        "energy": round(random.uniform(*b["energy"]), 1),
        "water": round(random.uniform(*b["water"]), 1),
    }


def generate_campus_data() -> pd.DataFrame:
    """Return a fresh DataFrame with one row per location."""
    rows = [_random_reading(loc) for loc in LOCATIONS]
    return pd.DataFrame(rows)


def inject_anomaly(df: pd.DataFrame, location: str = "Library") -> pd.DataFrame:
    """
    Force one location into an anomalous state.
    Used by the 'Simulate Emergency/Anomaly' demo button (Step 10).
    """
    df = df.copy()
    idx = df.index[df["location"] == location][0]
    df.loc[idx, "occupancy"] = 94.0
    df.loc[idx, "energy"] = 96.0
    df.loc[idx, "temperature"] = 30.0
    return df


def save_snapshot(df: pd.DataFrame, path: str = "data/campus_data.csv"):
    df.to_csv(path, index=False)


def generate_24h_history(location: str, metric: str = "energy") -> list:
    """
    Generate a plausible simulated last-24-hour trend for one
    location/metric, used for the historical trend chart. Deterministic
    per location+metric so the shape stays consistent within a session.
    """
    b = BASELINES[location][metric]
    mid = (b[0] + b[1]) / 2
    spread = (b[1] - b[0]) / 2
    rng = random.Random(f"{location}-{metric}")
    values = []
    for hour in range(24):
        # gentle day/night wave (higher mid-day) + noise, clipped at 0
        wave = spread * 0.5 * (1 - ((hour - 13) / 13) ** 2)
        noise = rng.uniform(-spread * 0.2, spread * 0.2)
        values.append(round(max(mid + wave + noise, 0), 1))
    return values


def generate_week_history(location: str, metric: str = "energy", seed_suffix: str = "") -> list:
    """
    Generate a full 7-day x 24-hour (168-point) simulated series for
    one location/metric, with a day/night wave plus a distinct
    weekday-vs-weekend level shift (see WEEKEND_FACTORS). Deterministic
    per location+metric+seed_suffix so the shape stays consistent
    within a session; pass a different seed_suffix to reshuffle it.
    """
    b = BASELINES[location][metric]
    mid = (b[0] + b[1]) / 2
    spread = (b[1] - b[0]) / 2
    rng = random.Random(f"week-{location}-{metric}-{seed_suffix}")
    weekend_factor = WEEKEND_FACTORS.get(location, 1.0) if metric != "temperature" else 1.0

    values = []
    for day in range(7):
        day_factor = weekend_factor if day >= 5 else 1.0
        for hour in range(24):
            wave = spread * 0.5 * (1 - ((hour - 13) / 13) ** 2)
            noise = rng.uniform(-spread * 0.15, spread * 0.15)
            value = (mid + wave) * day_factor + noise
            values.append(round(max(value, 0), 1))
    return values


def generate_week_dataframe(location: str = None, seed_suffix: str = "") -> pd.DataFrame:
    """
    Build a tidy 168-row-per-location DataFrame covering a full
    simulated week: day_index (0=Mon..6=Sun), day_name, is_weekend,
    hour, location, occupancy, temperature, energy, water. Pass a
    single location to build just that building's week, or leave it
    None for every location (used by the occupancy-vs-energy
    correlation chart).
    """
    locs = [location] if location else LOCATIONS
    rows = []
    for loc in locs:
        series = {
            m: generate_week_history(loc, m, seed_suffix)
            for m in ["occupancy", "temperature", "energy", "water"]
        }
        for i in range(168):
            day, hour = divmod(i, 24)
            rows.append({
                "location": loc,
                "day_index": day,
                "day_name": DAY_NAMES[day],
                "is_weekend": day >= 5,
                "hour": hour,
                "occupancy": series["occupancy"][i],
                "temperature": series["temperature"][i],
                "energy": series["energy"][i],
                "water": series["water"][i],
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_campus_data()
    save_snapshot(df)
    print(df)
