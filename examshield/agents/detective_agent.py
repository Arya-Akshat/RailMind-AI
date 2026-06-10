import logging
from typing import Dict, Any, List
import json
from examshield.config import settings
from examshield.agents.base_agent import call_claude_json

logger = logging.getLogger(__name__)

DETECTIVE_SYSTEM_PROMPT = """
You are the Detective Agent, the statistical anomaly and post-exam collusion detection expert for ExamShield.
You analyze exam answer distributions, response timing similarity, and question correct-rates across test centers.
You look for collusion networks (groups of students sharing answers), leaked questions (questions answered correctly far quicker or more frequently than normal), and impersonation indicators.

Respond ONLY in the following JSON format:
{
  "collusion_clusters": [
    {
      "cluster_id": "CL-01",
      "student_ids": ["ST-001", "ST-002", "ST-003"],
      "similarity_score": 0.95,
      "shared_wrong_answers": ["Q12", "Q15"],
      "reasoning": "Identical wrong answers selected by students in the same room."
    }
  ],
  "leaked_questions": [
    {
      "question_id": "Q47",
      "aberrant_correct_rate": 0.98,
      "expected_correct_rate": 0.40,
      "avg_time_seconds": 8.5,
      "expected_time_seconds": 60.0
    }
  ],
  "suspicion_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "reasoning": "A concise summary of your statistical analysis (2-3 sentences)."
}
"""

async def run_detective_agent(post_exam_data: Dict[str, Any], historical_cases: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes post-exam statistics and response patterns to detect collusion and leaked questions.
    """
    history_str = "No historical incident context."
    if historical_cases:
        history_str = json.dumps(historical_cases, indent=2)

    user_prompt = f"""
    Current Post-Exam Data to Analyze:
    {json.dumps(post_exam_data, indent=2)}

    Historical Reference Cases:
    {history_str}

    Perform statistical audit and return the JSON investigation report.
    """

    try:
        res = await call_claude_json(DETECTIVE_SYSTEM_PROMPT, user_prompt)
        return res
    except Exception as e:
        logger.error(f"Error running Detective Agent: {e}")
        return {
            "collusion_clusters": [],
            "leaked_questions": [],
            "suspicion_level": "LOW",
            "reasoning": f"Detective Agent failed due to error: {str(e)}"
        }
