import json
import logging
from anthropic import AsyncAnthropic
from examshield.config import settings

logger = logging.getLogger(__name__)

async def call_claude(system: str, user: str, max_tokens=600) -> str:
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("sk-ant-..."):
        # Fallback to mock generation if no API key is set
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
    Returns realistic mock JSON responses for the agent flow when offline or API key is absent.
    """
    # Detect which agent is calling by looking at the system prompt
    system_lower = system.lower()
    
    if "oracle agent" in system_lower:
        return json.dumps({
            "final_severity": "CRITICAL",
            "evidence_chain": [
                "Pre-Exam: Credential USR-OFFICER-DEV used from unauthorized IP 203.0.113.15 at 2:15 AM to decrypt papers.",
                "During-Exam: Student ST-002 showed high focus losses and answered Q47-Q50 in under 8 seconds.",
                "Post-Exam: Student ST-002 was clustered in collusion group CL-01, sharing 3 identical incorrect choices with 4 other candidates."
            ],
            "correlated_findings": "The pre-exam decryption matches the post-exam question anomaly for Q47. The leak was propagated to Center Delhi-12, resulting in classroom collusion.",
            "audit_trail_hash": "SHA256:d8a57e3f89ba578a7bde238faef96c6a8f8a65c2763261a8ef901235fa7c14a9",
            "remediation_plan": [
                "Cancel exam results for flagged student cluster (ST-002, ST-003, ST-004, ST-008, ST-011).",
                "Re-audit IP access controls for pre-exam vault.",
                "Initiate forensic investigation on credential owner USR-OFFICER-DEV."
            ]
        })
    elif "vault agent" in system_lower:
        return json.dumps({
            "suspicion_level": "CRITICAL",
            "anomalies_detected": [
                {
                    "type": "out_of_hours",
                    "details": "Unauthorized decryption and download of exam paper sets at 2:15 AM from an external IP address.",
                    "ip_address": "203.0.113.15",
                    "user_id": "USR-OFFICER-DEV"
                }
            ],
            "reasoning": "A download of 4.2GB of exam papers during off-hours from an external IP is highly suspicious and indicative of a pre-exam leak.",
            "remediation_actions": [
                "Immediately revoke access keys for KEY-NEET-UG-SET-B.",
                "Suspend and audit credentials for user USR-OFFICER-DEV.",
                "Verify logs for additional access from IP 203.0.113.15."
            ]
        })
        
    elif "watchdog agent" in system_lower:
        return json.dumps({
            "confidence_score": 0.95,
            "suspicion_level": "CRITICAL",
            "indicators": [
                {
                    "type": "gaze_deviation",
                    "severity": "high",
                    "details": "User exhibited 22 major gaze deviations during the examination period."
                },
                {
                    "type": "focus_loss",
                    "severity": "high",
                    "details": "User lost browser focus/tab-switched 14 times, potentially to view cheat sheets."
                },
                {
                    "type": "rapid_answering",
                    "severity": "high",
                    "details": "Questions Q47-Q50 were answered correctly in under 8 seconds per question."
                }
            ],
            "reasoning": "The combination of frequent focus losses, extreme gaze deviations, and answering complex questions in seconds suggests external help or pre-knowledge.",
            "recommended_action": "Immediate flag"
        })
        
    elif "detective agent" in system_lower:
        return json.dumps({
            "collusion_clusters": [
                {
                    "cluster_id": "CL-01",
                    "student_ids": ["ST-002", "ST-003", "ST-004", "ST-008", "ST-011"],
                    "similarity_score": 0.95,
                    "shared_wrong_answers": ["Q12", "Q15", "Q22"],
                    "reasoning": "Identical wrong answers selected by students in the same room (Room 3, Delhi Center)."
                }
            ],
            "leaked_questions": [
                {
                    "question_id": "Q47",
                    "aberrant_correct_rate": 0.96,
                    "expected_correct_rate": 0.38,
                    "avg_time_seconds": 7.2,
                    "expected_time_seconds": 90.0
                },
                {
                    "question_id": "Q48",
                    "aberrant_correct_rate": 0.94,
                    "expected_correct_rate": 0.42,
                    "avg_time_seconds": 8.0,
                    "expected_time_seconds": 90.0
                }
            ],
            "suspicion_level": "CRITICAL",
            "reasoning": "High similarity clustering in wrong answers and statistical anomaly in Q47 and Q48 correct rates point to organized collusion."
        })
        
    return "{}"
