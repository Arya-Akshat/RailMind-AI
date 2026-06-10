from agents.base import call_claude_json

SYSTEM_PROMPT = """You are the Commander agent in RailMind. You receive classified incidents and
decide the tactical response. You know that Dispatcher handles crew deployment,
Scheduler handles train rerouting, and Communicator handles passenger alerts.
For critical incidents, activate all three. For high, activate Dispatcher and
Scheduler. For medium, activate Dispatcher only. For low, activate Communicator
only. Always state your reasoning clearly.
"""

USER_PROMPT_TEMPLATE = """Incident classified:
ID: {incident_id}
Classification: {classification}
Severity: {severity}
Confidence: {confidence}
Location: {location}

Decide the response strategy.

Respond in this exact JSON format:
{{
  "activate_dispatcher": true|false,
  "activate_scheduler": true|false,
  "activate_communicator": true|false,
  "priority": "<immediate|urgent|standard>",
  "reasoning": "<your reasoning in 2-3 sentences>"
}}
"""

async def run_commander(incident_id: str, classification: str, severity: str, confidence: float, location: str) -> dict:
    """
    Runs the Commander agent.
    Returns:
        dict: containing keys "activate_dispatcher", "activate_scheduler", "activate_communicator", "priority", "reasoning"
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(
        incident_id=incident_id,
        classification=classification,
        severity=severity,
        confidence=confidence,
        location=location
    )
    result = await call_claude_json(SYSTEM_PROMPT, user_prompt)
    return result
