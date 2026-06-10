from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Any

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PhaseType(str, Enum):
    PRE_EXAM = "pre_exam"
    DURING_EXAM = "during_exam"
    POST_EXAM = "post_exam"

class ExamIncident(BaseModel):
    incident_id: str
    severity: SeverityLevel
    integrity_score: float  # 0.0 - 1.0 (where 0.0 is complete breach)
    evidence_chain: List[str]
    audit_trail_hash: str
    created_at: datetime
    resolved_at: datetime | None = None
    resolution_summary: str | None = None
    metadata_payload: Dict[str, Any]
