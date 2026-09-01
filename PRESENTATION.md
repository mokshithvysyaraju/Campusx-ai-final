# CAMPUSX AI — Presentation Script

**Project:** CAMPUSX AI — Smart Campus Simulator
**Flow:** Data → Detection → AI Analysis → Prediction → Action

---

## 1. Problem (30–40 sec)

> Colleges generate huge amounts of operational data — occupancy, energy,
> temperature, water — across dozens of buildings every single day. But
> almost none of it gets turned into action. Facilities teams find out
> about a wasteful AC running all night, or a water leak, only after
> the bill arrives or someone complains. The data exists. The
> intelligence to act on it doesn't.

---

## 2. Solution (30–40 sec)

> CAMPUSX AI creates a live simulated digital representation of campus
> operations — occupancy, energy, temperature, and water across five key
> buildings — and layers AI directly into that pipeline. It doesn't just
> show numbers on a dashboard. It automatically detects when something
> is abnormal, explains *why* it's likely happening, predicts what
> happens next, and recommends a specific action — all without a human
> having to go looking for the problem.

*(Optional: show the live dashboard here for a few seconds before the demo — home screen, campus map, all green.)*

---

## 3. Demo (60–90 sec — your main moment)

**Script while you click:**

1. "Right now, the campus is running normally — all buildings green, no alerts." *(point to status pill)*
2. "Let's simulate a real incident." → click **🚨 Simulate Anomaly**
3. "The Library just spiked — occupancy, energy, and temperature all jumped at once." *(point to the red building card)*
4. "The system catches it instantly — no one had to notice this manually." *(point to the anomaly alert)*
5. "And here's where it goes further than a normal dashboard — the AI Advisor doesn't just flag the anomaly, it explains what's likely causing it, predicts the impact, and tells facilities exactly what to do." *(read one line from the AI Advisor card)*
6. "And it doesn't stop at the present — it also forecasts where energy use is headed in the next few hours, so the team can act before it becomes a bigger problem." *(point to the prediction chart)*

---

## 4. Innovation (20–30 sec)

> We're deliberately not using AI as a chatbot bolted onto a dashboard.
> The AI is embedded directly into the operational pipeline — it reacts
> to the data itself, forming the connective layer between "here's a
> number" and "here's what to do about it." That's the difference
> between a monitoring tool and a decision-support system.

---

## 5. Future Scope (20–30 sec)

> This is a working simulation today, but the architecture is built to
> extend into a full campus digital twin:
> - Real IoT sensors replacing simulated data
> - CCTV / computer vision for occupancy instead of estimates
> - Real-time live campus data feeds
> - Deeper energy optimization models
> - Predictive maintenance for equipment before it fails
> - A mobile app for facilities staff to get alerts on the go

---

## Quick Q&A prep

**"Is this using real data?"**
No — it's simulated for the prototype, but the pipeline (detection → AI
analysis → prediction → action) is built to plug into real sensor data
without changing the architecture.

**"What AI model powers the advisor?"**
It calls an LLM (Claude) to generate the explanation and
recommendation for each anomaly, with a rule-based fallback so the
demo never breaks if the API is unavailable.

**"How does anomaly detection work?"**
Right now it's threshold-based — comparing live readings against
expected baseline ranges per building. That's intentional for a
reliable, explainable MVP; it's built so a proper ML model can slot in
later without touching the rest of the app.

**"Why only 5 buildings / limited metrics?"**
Scope was kept deliberately small to build something that works
extremely well end-to-end, rather than a broad system that's shallow
everywhere.
