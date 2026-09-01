"""
sustainability.py — Cost & Sustainability framing for CAMPUSX AI

Converts simulated energy readings (kWh) into rupee cost and CO2
estimates, projects the ₹/CO2 at stake if an energy anomaly is left
unresolved, and derives a per-building "Green Score" so buildings can
be ranked by efficiency.

The tariff and grid-emission-factor constants below are reasonable
demo assumptions (an institutional/commercial electricity tariff and
India's approximate grid-average CO2 intensity per the CEA CO2
baseline database). Both are exposed as sliders in app.py — swap in
the campus's actual DISCOM tariff slab and a current CEA factor for
a real deployment.
"""

from data import BASELINES, LOCATIONS

DEFAULT_RATE_PER_KWH = 8.0     # ₹/kWh — approx institutional tariff
DEFAULT_CO2_PER_KWH = 0.82     # kg CO2/kWh — approx India grid average


def energy_to_cost(kwh: float, rate: float = DEFAULT_RATE_PER_KWH) -> float:
    """Estimated ₹ cost for a given kWh reading."""
    return round(kwh * rate, 2)


def energy_to_co2(kwh: float, factor: float = DEFAULT_CO2_PER_KWH) -> float:
    """Estimated kg CO2 for a given kWh reading."""
    return round(kwh * factor, 2)


def anomaly_savings(
    location: str,
    current_kwh: float,
    rate: float = DEFAULT_RATE_PER_KWH,
    co2_factor: float = DEFAULT_CO2_PER_KWH,
    hours_quick: float = 1.0,
    hours_delay: float = 24.0,
) -> dict:
    """
    Estimate the ₹ / kWh / CO2 being wasted per hour by an energy
    anomaly (energy above the building's normal baseline ceiling),
    and project it across a "fix it now" window vs. a "left
    unresolved" window — used by the AI Advisor to show what's at
    stake.
    """
    high = BASELINES[location]["energy"][1]
    excess_per_hour = max(current_kwh - high, 0.0)

    return {
        "excess_kwh_per_hour": round(excess_per_hour, 1),
        "hours_quick": hours_quick,
        "hours_delay": hours_delay,
        "quick_fix_kwh": round(excess_per_hour * hours_quick, 1),
        "quick_fix_cost": energy_to_cost(excess_per_hour * hours_quick, rate),
        "quick_fix_co2": energy_to_co2(excess_per_hour * hours_quick, co2_factor),
        "delayed_kwh": round(excess_per_hour * hours_delay, 1),
        "delayed_cost": energy_to_cost(excess_per_hour * hours_delay, rate),
        "delayed_co2": energy_to_co2(excess_per_hour * hours_delay, co2_factor),
    }


def green_score(location: str, current_kwh: float) -> int:
    """
    0-100 efficiency score for a building's current energy reading,
    relative to its own baseline band:
      - at/under the low end of the band  -> 100
      - at the high end of the band       -> 60
      - beyond the high end               -> falls steeply toward 0
    """
    low, high = BASELINES[location]["energy"]
    span = max(high - low, 1e-6)

    if current_kwh <= low:
        score = 100.0
    elif current_kwh <= high:
        score = 100 - (current_kwh - low) / span * 40
    else:
        score = 60 - (current_kwh - high) / span * 60

    return int(round(max(0, min(100, score))))


def green_grade(score: int) -> str:
    """Compact letter grade for a green score."""
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 30:
        return "D"
    return "F"


def rank_buildings(df, rate: float = DEFAULT_RATE_PER_KWH, co2_factor: float = DEFAULT_CO2_PER_KWH) -> list[dict]:
    """
    Given the campus dataframe, return one dict per building — sorted
    by Green Score descending — with location, energy, cost, co2,
    score, grade, and rank.
    """
    rows = []
    for _, row in df.iterrows():
        loc, kwh = row["location"], row["energy"]
        score = green_score(loc, kwh)
        rows.append({
            "location": loc,
            "energy": kwh,
            "cost": energy_to_cost(kwh, rate),
            "co2": energy_to_co2(kwh, co2_factor),
            "score": score,
            "grade": green_grade(score),
        })
    rows.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows


if __name__ == "__main__":
    from data import generate_campus_data

    df = generate_campus_data()
    for r in rank_buildings(df):
        print(r)
