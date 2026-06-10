from agents.base import call_claude_json
from models.incident import TrainReroute

SYSTEM_PROMPT = """You are the Scheduler agent in RailMind. You reroute trains away from
compromised track sections. You understand Indian Railway network topology.
Minimise total passenger delay across the network. Prefer diversions via
existing alternate routes over full cancellations. Always state the
delay impact clearly.
"""

USER_PROMPT_TEMPLATE = """Track section compromised:
Incident ID: {incident_id}
Location: {location}
Classification: {classification}
Estimated repair time: {eta_minutes} minutes

Affected trains (simulated):
- Train 12951 Rajdhani Express: Next stop affected section in 18 min
- Train 22119 Tejas Express: Next stop affected section in 34 min
- Train 19019 Saurashtra Mail: Next stop affected section in 52 min

Compute reroutes for all affected trains.

Respond in this exact JSON format:
{{
  "reroutes": [
    {{
      "train_id": "<train number>",
      "original_route": "<original route segment>",
      "new_route": "<alternate route>",
      "delay_minutes": <integer>,
      "reason": "<one sentence>"
    }}
  ],
  "total_passengers_affected": <integer estimate>,
  "reasoning": "<your reasoning in 2-3 sentences>"
}}
"""

async def run_scheduler(incident_id: str, location: str, classification: str, eta_minutes: int) -> tuple[list[TrainReroute], dict]:
    """
    Runs the Scheduler agent.
    Returns:
        tuple[list[TrainReroute], dict]: (list of TrainReroute instances, original agent response dict containing reasoning/summary)
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(
        incident_id=incident_id,
        location=location,
        classification=classification,
        eta_minutes=eta_minutes
    )
    
    result = await call_claude_json(SYSTEM_PROMPT, user_prompt)
    
    reroutes = []
    for r in result.get("reroutes", []):
        reroutes.append(
            TrainReroute(
                train_id=r.get("train_id", "UNKNOWN"),
                original_route=r.get("original_route", "Direct"),
                new_route=r.get("new_route", "Diverted"),
                delay_minutes=int(r.get("delay_minutes", 0)),
                reason=r.get("reason", "Rerouted due to incident")
            )
        )
        
    return reroutes, result
