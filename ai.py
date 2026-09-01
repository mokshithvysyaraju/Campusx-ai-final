"""
ai.py — AI Advisor (Step 8)

Sends a detected anomaly to an LLM and asks for:
1. What happened
2. Possible reason
3. Predicted impact
4. Recommended action

Set your API key as an environment variable before running:
    export ANTHROPIC_API_KEY=sk-ant-...        (Mac/Linux)
    setx ANTHROPIC_API_KEY "sk-ant-..."         (Windows)

If no key is set, a rule-based fallback explanation is used instead,
so the app still runs/demos without an API key.
"""

import os
import json

SYSTEM_PROMPT = """You are an AI operations advisor for a smart campus \
monitoring system. Given a single detected anomaly, respond ONLY with a \
JSON object (no markdown, no preamble) with these exact keys:
{
  "what_happened": "...",
  "possible_cause": "...",
  "predicted_impact": "...",
  "recommendation": "...",
  "priority": "Low" | "Medium" | "High"
}
Keep each value to one short sentence."""


def _fallback_explanation(anomaly: dict) -> dict:
    """No API key available — simple rule-based stand-in."""
    metric = anomaly["metric"]
    loc = anomaly["location"]
    value = anomaly["value"]
    high = anomaly["expected_high"]
    direction = "above" if value > high else "below"

    return {
        "what_happened": f"{metric.title()} at {loc} is {value}, {direction} the expected range.",
        "possible_cause": "Unusual usage pattern or equipment inefficiency.",
        "predicted_impact": "Continued deviation may raise costs or reduce comfort/safety.",
        "recommendation": f"Inspect {loc}'s {metric} systems and adjust settings.",
        "priority": "Medium",
    }


def get_ai_recommendation(anomaly: dict) -> dict:
    """
    Given one anomaly dict from detector.py, return an explanation dict.
    Tries the Anthropic API first; falls back to a rule-based response
    if no API key is configured or the call fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_explanation(anomaly)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        user_message = (
            f"Anomaly detected:\n"
            f"Location: {anomaly['location']}\n"
            f"Metric: {anomaly['metric']}\n"
            f"Current value: {anomaly['value']}\n"
            f"Expected range: {anomaly['expected_low']}–{anomaly['expected_high']}"
        )

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    except Exception as e:
        result = _fallback_explanation(anomaly)
        result["what_happened"] += f" (AI call failed, using fallback: {e})"
        return result


if __name__ == "__main__":
    sample_anomaly = {
        "location": "Library",
        "metric": "energy",
        "value": 96,
        "expected_low": 40,
        "expected_high": 70,
    }
    print(get_ai_recommendation(sample_anomaly))
