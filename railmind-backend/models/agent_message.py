from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from models.incident import Incident

class AgentStep(BaseModel):
    message_type: Literal["agent_step"]
    step_id: str           # UUID
    agent_name: Literal["Sentinel", "Commander", "Dispatcher", "Scheduler", "Communicator"]
    incident_id: str
    thought: str           # Claude's reasoning
    action: str            # short label of what the agent decided to do
    output: dict           # structured result specific to each agent
    timestamp: datetime
    is_final: bool         # True on the last step of a resolution pipeline

class IncidentCreated(BaseModel):
    message_type: Literal["incident_created"]
    incident: Incident

class ResolutionComplete(BaseModel):
    message_type: Literal["resolution_complete"]
    incident_id: str
    duration_seconds: float
    summary: str

class ErrorMessage(BaseModel):
    message_type: Literal["error"]
    detail: str
