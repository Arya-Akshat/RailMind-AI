import uuid
from datetime import datetime
from agents.base import call_claude_json
from models.incident import WorkOrder

SYSTEM_PROMPT = """You are the Dispatcher agent in RailMind. You assign maintenance crews to
incidents. You have access to a simulated crew registry. Choose the most
appropriate crew based on incident type and location. Create actionable
work orders with realistic ETAs based on Indian Railway geography.
"""

USER_PROMPT_TEMPLATE = """Incident requires crew dispatch:
ID: {incident_id}
Classification: {classification}
Severity: {severity}
Location: {location}
Priority: {priority}

Available crews (simulated):
- Crew ALPHA-7: Track maintenance specialists, currently at Mumbai Central (35 min from corridor)
- Crew BETA-3: Signal engineers, currently at Pune Junction (55 min from corridor)
- Crew GAMMA-1: Emergency response unit, currently at Surat depot (25 min from corridor)
- Crew DELTA-9: General maintenance, currently at Vadodara (45 min from corridor)

Assign a crew and create a work order.

Respond in this exact JSON format:
{{
  "crew_id": "<crew identifier>",
  "action": "<specific action the crew must take>",
  "eta_minutes": <integer>,
  "work_order_summary": "<one sentence summary>",
  "reasoning": "<your reasoning in 1-2 sentences>"
}}
"""

async def run_dispatcher(incident_id: str, classification: str, severity: str, location: str, priority: str) -> tuple[WorkOrder, dict]:
    """
    Runs the Dispatcher agent.
    Returns:
        tuple[WorkOrder, dict]: (WorkOrder instance, original agent response dict containing reasoning/summary)
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(
        incident_id=incident_id,
        classification=classification,
        severity=severity,
        location=location,
        priority=priority
    )
    
    result = await call_claude_json(SYSTEM_PROMPT, user_prompt)
    
    work_order = WorkOrder(
        work_order_id=f"WO-{uuid.uuid4().hex[:8].upper()}",
        incident_id=incident_id,
        crew_id=result.get("crew_id", "UNKNOWN"),
        action=result.get("action", "Inspect site"),
        eta_minutes=int(result.get("eta_minutes", 60)),
        created_at=datetime.utcnow()
    )
    
    return work_order, result
