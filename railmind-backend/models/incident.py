from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SensorEvent(BaseModel):
    event_id: str          # UUID
    timestamp: datetime
    sensor_type: str       # e.g. "vibration", "thermal", "acoustic"
    location: str          # e.g. "Section 47B, Delhi-Mumbai corridor"
    reading: float
    threshold: float
    raw_payload: dict

class Incident(BaseModel):
    incident_id: str
    sensor_event: SensorEvent
    severity: SeverityLevel
    classification: str    # e.g. "rail_fracture", "signal_failure"
    confidence: float      # 0.0–1.0
    created_at: datetime
    resolved_at: datetime | None = None
    resolution_summary: str | None = None

class WorkOrder(BaseModel):
    work_order_id: str
    incident_id: str
    crew_id: str
    action: str
    eta_minutes: int
    created_at: datetime

class TrainReroute(BaseModel):
    train_id: str
    original_route: str
    new_route: str
    delay_minutes: int
    reason: str
