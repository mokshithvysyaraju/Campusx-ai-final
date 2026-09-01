"""
detector.py — Simple rule-based anomaly detection (Step 7)

Deliberately simple: compares each reading against the expected
BASELINES range from data.py. No ML needed for the MVP — this can be
swapped for a scikit-learn model later without changing app.py.
"""

import pandas as pd
from data import BASELINES

# How far outside the baseline range counts as an anomaly (in %)
TOLERANCE = 0.15  # 15% beyond the min/max edge


def _is_out_of_range(value: float, low: float, high: float, tolerance: float = TOLERANCE) -> bool:
    margin = (high - low) * tolerance
    return value < (low - margin) or value > (high + margin)


def detect_anomalies(df: pd.DataFrame, tolerance: float = TOLERANCE) -> list[dict]:
    """
    Scan every row/metric against its baseline.
    `tolerance` controls sensitivity (lower = stricter, matches the
    live Settings panel in app.py). Returns a list of anomaly dicts:
    {location, metric, value, expected_low, expected_high}
    """
    anomalies = []
    for _, row in df.iterrows():
        loc = row["location"]
        baseline = BASELINES[loc]
        for metric in ["occupancy", "temperature", "energy", "water"]:
            low, high = baseline[metric]
            value = row[metric]
            if _is_out_of_range(value, low, high, tolerance):
                anomalies.append({
                    "location": loc,
                    "metric": metric,
                    "value": value,
                    "expected_low": low,
                    "expected_high": high,
                })
    return anomalies


if __name__ == "__main__":
    from data import generate_campus_data, inject_anomaly

    df = inject_anomaly(generate_campus_data(), "Library")
    for a in detect_anomalies(df):
        print(a)
