import logging
from typing import Dict, Any, List
import json
from examshield.config import settings
from examshield.agents.base_agent import call_claude_json

logger = logging.getLogger(__name__)

ORACLE_SYSTEM_PROMPT = """
You are the Oracle Agent, the central orchestrator and final report generator of ExamShield.
Your role is to correlate findings from all three phases:
1. Pre-Exam (Vault Agent) - e.g. unauthorized paper access
2. During-Exam (Watchdog Agent) - e.g. suspicious student behavior, high cheating confidence
3. Post-Exam (Detective Agent) - e.g. collusion clusters and question leaks

You correlate these signals into a unified, evidence-backed investigation report. For example, you trace if a student who showed high cheating confidence or was part of a collusion cluster also fits into a pre-exam data breach pattern.
You assign a final incident severity level ("LOW", "MEDIUM", "HIGH", "CRITICAL").

Respond ONLY in the following JSON format:
{
  "final_severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "evidence_chain": [
    "Pre-exam: IP 192.168.1.5 accessed exam vault at 2:00 AM.",
    "During exam: Student ST-002 flagged for high gaze deviation (0.90 confidence).",
    "Post-exam: Student ST-002 was clustered with ST-003 and ST-004, sharing 3 identical incorrect answers."
  ],
  "correlated_findings": "Detailed description of how the pre-exam, during-exam, and post-exam events connect to reveal the fraud mechanism.",
  "audit_trail_hash": "A unique mock signature of the integrity audit",
  "remediation_plan": [
    "Cancel exam results for flagged student cluster.",
    "Re-audit IP access controls for pre-exam vault.",
    "Inspect the physical exam center for local wireless transmitters."
  ]
}
"""

async def run_oracle_agent(
    vault_findings: Dict[str, Any],
    watchdog_findings: List[Dict[str, Any]],
    detective_findings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Correlates the findings of Vault, Watchdog, and Detective agents, then produces a final, audited integrity report.
    """
    user_prompt = f"""
    === VAULT AGENT FINDINGS (PRE-EXAM) ===
    {json.dumps(vault_findings, indent=2)}

    === WATCHDOG AGENT FINDINGS (DURING-EXAM) ===
    {json.dumps(watchdog_findings, indent=2)}

    === DETECTIVE AGENT FINDINGS (POST-EXAM) ===
    {json.dumps(detective_findings, indent=2)}

    Analyze the complete dossier. Formulate a unified evidence chain and remediation plan. Return the JSON report.
    """

    try:
        res = await call_claude_json(ORACLE_SYSTEM_PROMPT, user_prompt)
        return res
    except Exception as e:
        logger.error(f"Error running Oracle Agent: {e}")
        return {
            "final_severity": "LOW",
            "evidence_chain": [f"Orchestrator failed during compilation: {str(e)}"],
            "correlated_findings": "Failed to generate correlation report due to system error.",
            "audit_trail_hash": "ERROR_SIG",
            "remediation_plan": ["Manually review all phase logs."]
        }
