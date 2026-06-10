import logging
from typing import Dict, Any, List
import json
from examshield.config import settings
from examshield.agents.base_agent import call_claude_json

logger = logging.getLogger(__name__)

WATCHDOG_SYSTEM_PROMPT = """
You are the Watchdog Agent, the real-time proctoring and behavioral analysis specialist for ExamShield.
You monitor active students during the exam. You analyze logs containing keystroke dynamics, focus/tab switching history, gaze/facial orientation flags, and question timing.
You calculate a confidence score (from 0.0 to 1.0) indicating the probability of integrity violation.
You do not make binary decisions; you provide a confidence score and document the exact indicators.

Respond ONLY in the following JSON format:
{
  "confidence_score": 0.85,
  "suspicion_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "indicators": [
    {
      "type": "keystroke_anomaly" | "focus_loss" | "gaze_deviation" | "rapid_answering" | "other",
      "severity": "low" | "medium" | "high",
      "details": "Explanation of the indicator"
    }
  ],
  "reasoning": "A concise summary of your analysis (2-3 sentences).",
  "recommended_action": "Proctor review" | "Immediate flag" | "Allow to continue"
}
"""

async def run_watchdog_agent(student_session_log: Dict[str, Any], historical_patterns: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes student exam logs in real-time to detect cheating behavior and compute a confidence score.
    """
    history_str = "No historical incident context."
    if historical_patterns:
        history_str = json.dumps(historical_patterns, indent=2)

    user_prompt = f"""
    Current Student Session Log to Analyze:
    {json.dumps(student_session_log, indent=2)}

    Historical Reference Cases:
    {history_str}

    Evaluate the session log and return the JSON proctoring report.
    """

    try:
        res = await call_claude_json(WATCHDOG_SYSTEM_PROMPT, user_prompt)
        return res
    except Exception as e:
        logger.error(f"Error running Watchdog Agent: {e}")
        return {
            "confidence_score": 0.0,
            "suspicion_level": "LOW",
            "indicators": [],
            "reasoning": f"Watchdog Agent failed due to error: {str(e)}",
            "recommended_action": "Allow to continue"
        }
