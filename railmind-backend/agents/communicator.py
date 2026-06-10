from agents.base import call_claude_json

SYSTEM_PROMPT = """You are the Communicator agent in RailMind. You draft clear, calm, and
accurate passenger-facing alerts and internal staff notifications. Passenger
messages must be non-alarming, factual, and include actionable guidance.
Staff notifications must be direct and include all operational details.
Write in both English and include a note that Hindi translation should follow.
"""

USER_PROMPT_TEMPLATE = """Incident resolved/in-progress, alerts required:
Incident ID: {incident_id}
Classification: {classification}
Location: {location}
Affected trains: {affected_trains}
Reroutes: {reroutes}
Crew dispatched: {crew_id}, ETA: {eta_minutes} min

Draft:
1. A passenger SMS alert (max 160 characters)
2. A station master notification (2-3 sentences, operational tone)

Respond in this exact JSON format:
{{
  "passenger_sms": "<max 160 chars>",
  "station_master_notification": "<2-3 sentences>",
  "channels": ["SMS", "PA system", "station display boards"]
}}
"""

async def run_communicator(
    incident_id: str,
    classification: str,
    location: str,
    affected_trains: str = "None",
    reroutes: str = "None",
    crew_id: str = "None",
    eta_minutes: int = 0
) -> dict:
    """
    Runs the Communicator agent.
    Returns:
        dict: containing keys "passenger_sms", "station_master_notification", "channels"
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(
        incident_id=incident_id,
        classification=classification,
        location=location,
        affected_trains=affected_trains,
        reroutes=reroutes,
        crew_id=crew_id,
        eta_minutes=eta_minutes
    )
    result = await call_claude_json(SYSTEM_PROMPT, user_prompt)
    return result
