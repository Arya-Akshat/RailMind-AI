import json
import logging
from anthropic import AsyncAnthropic
from config import settings

logger = logging.getLogger(__name__)

async def call_claude(system: str, user: str, max_tokens=600) -> str:
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("sk-ant-..."):
        return get_mock_response(system, user)
        
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    msg = await client.messages.create(
        model=settings.MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    return msg.content[0].text

async def call_claude_json(system: str, user: str, max_tokens=600) -> dict:
    try:
        response = await call_claude(system, user, max_tokens)
        return _parse_json(response)
    except Exception as e:
        logger.warning(f"JSON call failed: {e}. Retrying once with JSON correction prompt...")
        correction_user = (
            f"{user}\n\n"
            "Your previous response was not valid JSON. Return only the JSON object "
            "with no additional conversational filler or markdown markers."
        )
        try:
            response = await call_claude(system, correction_user, max_tokens)
            return _parse_json(response)
        except Exception as e_retry:
            logger.error(f"Retry JSON parsing failed: {e_retry}")
            raise e_retry

def _parse_json(text: str) -> dict:
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    
    clean_text = clean_text.strip()
    return json.loads(clean_text)

def get_mock_response(system: str, user: str) -> str:
    """
    Returns realistic mock JSON responses for the RailMind agent flow when offline or API key is absent.
    """
    system_lower = system.lower()
    
    if "sentinel" in system_lower:
        return json.dumps({
            "classification": "rail_fracture",
            "severity": "critical",
            "confidence": 0.94,
            "reasoning": "Vibration frequency of 142Hz with 9.4mm amplitude is a clear indicator of a rail fracture on Section 47B."
        })
        
    elif "commander" in system_lower:
        return json.dumps({
            "activate_dispatcher": True,
            "activate_scheduler": True,
            "activate_communicator": True,
            "priority": "immediate",
            "reasoning": "A critical rail fracture on the Western Corridor requires immediate dispatcher deployment, train reroutes, and passenger notifications."
        })
        
    elif "dispatcher" in system_lower:
        return json.dumps({
            "crew_id": "Crew GAMMA-1",
            "action": "Dispatch emergency response unit to repair rail fracture at Section 47B.",
            "eta_minutes": 25,
            "work_order_summary": "Crew GAMMA-1 dispatched to Section 47B.",
            "reasoning": "Crew GAMMA-1 is the nearest emergency response unit located at the Surat depot (25 mins away)."
        })
        
    elif "scheduler" in system_lower:
        return json.dumps({
            "reroutes": [
                {
                    "train_id": "Train 12951 Rajdhani Express",
                    "original_route": "Mumbai-Delhi Western Corridor",
                    "new_route": "Diverted via Godhra-Ratlam line",
                    "delay_minutes": 35,
                    "reason": "Diverted due to rail fracture on main line"
                },
                {
                    "train_id": "Train 22119 Tejas Express",
                    "original_route": "Mumbai-Delhi Western Corridor",
                    "new_route": "Diverted via Godhra-Ratlam line",
                    "delay_minutes": 40,
                    "reason": "Diverted due to rail fracture on main line"
                }
            ],
            "total_passengers_affected": 2400,
            "reasoning": "Rerouted Rajdhani and Tejas Expresses to prevent delays and maintain safety."
        })
        
    elif "communicator" in system_lower:
        return json.dumps({
            "passenger_sms": "ALERT: Train 12951 & 22119 delayed by 35-40 mins due to track maintenance. Alternate routes scheduled.",
            "station_master_notification": "URGENT: Track fracture at Section 47B. Crew GAMMA-1 dispatched (ETA 25m). Reroute Rajdhani/Tejas via Godhra.",
            "channels": ["SMS", "PA system", "station display boards"]
        })
        
    return "{}"
