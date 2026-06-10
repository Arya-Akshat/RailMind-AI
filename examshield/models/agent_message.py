from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from examshield.models.incident import ExamIncident

class AgentStep(BaseModel):
    message_type: Literal["agent_step"]
    step_id: str
    agent_name: Literal["Vault", "Watchdog", "Detective", "Oracle"]
    incident_id: str
    thought: str
    action: str
    output: dict
    timestamp: datetime
    is_final: bool

class IncidentCreated(BaseModel):
    message_type: Literal["incident_created"]
    incident: ExamIncident

class ResolutionComplete(BaseModel):
    message_type: Literal["resolution_complete"]
    incident_id: str
    duration_seconds: float
    summary: str

class ErrorMessage(BaseModel):
    message_type: Literal["error"]
    detail: str
