from agents.base import call_claude_json
from models.incident import SensorEvent

SYSTEM_PROMPT = """You are the Sentinel agent in RailMind, an autonomous railway operations system.
You receive raw sensor readings from trackside sensors and classify them into
structured incidents. You are precise, conservative, and always explain your
confidence level. When in doubt, escalate severity — false positives are
preferable to missed detections in a safety-critical system.
"""

USER_PROMPT_TEMPLATE = """A sensor event has been received. Classify this as a railway incident.

Sensor type: {sensor_type}
Location: {location}
Reading: {reading} (threshold: {threshold})
Raw payload: {raw_payload}

Similar past incidents for reference:
{similar_incidents}

Respond in this exact JSON format:
{{
  "classification": "<rail_fracture|signal_failure|track_obstruction|thermal_anomaly|vibration_anomaly>",
  "severity": "<low|medium|high|critical>",
  "confidence": <0.0-1.0>,
  "reasoning": "<your reasoning in 2-3 sentences>"
}}
"""

async def run_sentinel(sensor_event: SensorEvent, similar_incidents: list[dict]) -> dict:
    """
    Runs the Sentinel agent.
    Returns:
        dict: containing keys "classification", "severity", "confidence", "reasoning"
    """
    # Format similar incidents text
    if not similar_incidents:
        similar_incidents_str = "No similar past incidents found in memory."
    else:
        similar_incidents_str = ""
        for i, inc in enumerate(similar_incidents, 1):
            similar_incidents_str += (
                f"{i}. ID: {inc['incident_id']} | Classification: {inc['classification']} | "
                f"Location: {inc['location']} | Summary: {inc['resolution_summary']}\n"
            )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        sensor_type=sensor_event.sensor_type,
        location=sensor_event.location,
        reading=sensor_event.reading,
        threshold=sensor_event.threshold,
        raw_payload=sensor_event.raw_payload,
        similar_incidents=similar_incidents_str
    )

    result = await call_claude_json(SYSTEM_PROMPT, user_prompt)
    return result
