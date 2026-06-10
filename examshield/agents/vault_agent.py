import logging
from typing import Dict, Any, List
import json
from examshield.config import settings
from examshield.db.postgres import get_pool
from examshield.agents.base_agent import call_claude_json

logger = logging.getLogger(__name__)

VAULT_SYSTEM_PROMPT = """
You are the Vault Agent, the security and integrity guardian for the pre-exam phase of ExamShield.
Your role is to monitor logs, access requests, paper generation pipelines, and transport logs to detect anomalies or leaks before the exam starts.
You analyze metadata such as IP addresses, access time, user roles, download volumes, and file decryption keys.

Analyze the provided log and flag any anomalies.
Rate the suspicion level as "LOW", "MEDIUM", "HIGH", or "CRITICAL".
Provide an evidence log of what you found and an audit report.

Respond ONLY in the following JSON format:
{
  "suspicion_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "anomalies_detected": [
    {
      "type": "unauthorized_access" | "bulk_download" | "out_of_hours" | "key_leak" | "other",
      "details": "Explanation of the anomaly",
      "ip_address": "IP involved",
      "user_id": "User involved"
    }
  ],
  "reasoning": "A concise summary of your analysis (2-3 sentences).",
  "remediation_actions": ["Action 1", "Action 2"]
}
"""

async def run_vault_agent(pre_exam_log: Dict[str, Any], historical_logs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes pre-exam access logs to flag potential leaks, unauthorized access, or unusual patterns.
    """
    history_str = "No historical incident context."
    if historical_logs:
        history_str = json.dumps(historical_logs, indent=2)

    user_prompt = f"""
    Current Pre-Exam Log Segment to Analyze:
    {json.dumps(pre_exam_log, indent=2)}

    Historical Reference Incidents:
    {history_str}

    Evaluate the risks and return the JSON report.
    """

    try:
        res = await call_claude_json(VAULT_SYSTEM_PROMPT, user_prompt)
        return res
    except Exception as e:
        logger.error(f"Error running Vault Agent: {e}")
        return {
            "suspicion_level": "LOW",
            "anomalies_detected": [],
            "reasoning": f"Vault Agent failed due to error: {str(e)}",
            "remediation_actions": ["Alert system administrator to check Vault logs manually."]
        }
