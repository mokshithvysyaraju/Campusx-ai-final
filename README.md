# CampusX AI — Smart Campus Simulator

A live simulated digital twin of campus operations that doesn't just show data — it detects anomalies, explains what's likely causing them, predicts what happens next, and recommends a specific action. No one has to go looking for the problem.

**Flow:** `Data → Detection → AI Analysis → Prediction → Action`

## The Problem

Colleges generate huge amounts of operational data — occupancy, energy, temperature, water — across dozens of buildings every day. Almost none of it gets turned into action. Facilities teams usually find out about a wasteful AC running all night, or a water leak, only after the bill arrives or someone complains.

## The Solution

CampusX AI simulates live operational data across five key buildings and layers AI directly into that pipeline, rather than bolting a chatbot onto a dashboard:

- **Detects** — a rule-based check flags any reading that falls outside its building's expected baseline range.
- **Explains** — an AI Advisor (powered by the Anthropic API) generates the likely cause and predicted impact for each anomaly, in plain language.
- **Predicts** — a lightweight regression model forecasts energy use a few hours ahead.
- **Acts** — the system recommends a specific, human-readable next step for facilities staff.

## Features

- 🗺️ Live campus overview — Block A, Block B, Library, Canteen, and Hostel, color-coded by status
- 🚨 Instant anomaly detection against per-building baseline ranges
- 🤖 AI Advisor: cause, predicted impact, and recommended action for every anomaly
- 📈 Short-term energy forecast chart
- 🎮 "Simulate Anomaly" button to trigger a live incident for demos
- 🛡️ Rule-based fallback so the app runs fully even without an API key

## Tech Stack

| Tool | Role |
|---|---|
| [Streamlit](https://streamlit.io) | Dashboard UI |
| [Pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org) | Data simulation & wrangling |
| [Plotly](https://plotly.com) | Charts and campus map |
| [scikit-learn](https://scikit-learn.org) | `LinearRegression` energy forecast |
| [Anthropic API](https://www.anthropic.com) | AI Advisor (Claude) |

## Getting Started

### Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com) (optional — the app falls back to rule-based explanations without one)

### Installation

```bash
git clone https://github.com/<your-username>/CampusX-App.git
cd CampusX-App/AI-Smart-Campus
pip install -r requirements.txt
```

### Configuration

Set your Anthropic API key as an environment variable to enable AI-generated explanations:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows
setx ANTHROPIC_API_KEY "sk-ant-..."
```

Without a key, the AI Advisor automatically uses a deterministic rule-based explanation instead, so the app still runs end-to-end.

### Run

```bash
streamlit run app.py
```

## Project Structure

```
AI-Smart-Campus/
├── app.py              # Streamlit dashboard — layout, map, drill-down, prediction
├── data.py              # Simulated campus data generator + baselines
├── detector.py           # Rule-based anomaly detection
├── ai.py                # AI Advisor (Anthropic API + rule-based fallback)
├── icons.py              # Icon helpers for the UI
├── .streamlit/config.toml # Dashboard theme
├── requirements.txt
└── PRESENTATION.md        # Pitch/demo script
```

## How Anomaly Detection Works

Each reading (occupancy, temperature, energy, water) is compared against a baseline range defined per building in `data.py`. A reading counts as anomalous if it falls outside that range by more than a **15% tolerance** margin. This is deliberately simple and explainable for the MVP — the same interface can be swapped for a real ML model later without touching the rest of the app.

## Roadmap

This is a working simulation today, with an architecture built to extend into a full campus digital twin:

- [ ] Real IoT sensors replacing simulated data
- [ ] CCTV / computer vision for real occupancy counts
- [ ] Live real-time campus data feeds
- [ ] Deeper energy optimization models
- [ ] Predictive maintenance for equipment before it fails
- [ ] Mobile app for facilities staff alerts

## FAQ

**Is this using real data?**
No — it's simulated for the prototype, but the pipeline (detection → AI analysis → prediction → action) is built to plug into real sensor data without changing the architecture.

**What AI model powers the advisor?**
It calls the Anthropic API (Claude) to generate the explanation and recommendation for each anomaly, with a rule-based fallback so the demo never breaks if the API is unavailable.

**Why only 5 buildings / a handful of metrics?**
Scope was kept deliberately small to build something that works extremely well end-to-end, rather than something broad but shallow.


