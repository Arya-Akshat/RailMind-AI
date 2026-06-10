import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from examshield.models.incident import ExamIncident, SeverityLevel
from examshield.agents.vault_agent import run_vault_agent
from examshield.agents.watchdog_agent import run_watchdog_agent
from examshield.agents.detective_agent import run_detective_agent
from examshield.agents.oracle_agent import run_oracle_agent
from examshield.graph.orchestrator import app_graph, ExamShieldState

@pytest.fixture
def sample_vault_log():
    return {
        "event_id": "PR-0491",
        "timestamp": "2026-06-10T02:15:22Z",
        "user_id": "USR-OFFICER-DEV",
        "role": "Exam Custodian",
        "ip_address": "203.0.113.15",
        "location": "Delhi Main Vault Server",
        "action": "DECRYPT_AND_DOWNLOAD",
        "download_size_gb": 4.2,
        "key_id": "KEY-NEET-UG-SET-B"
    }

@pytest.fixture
def sample_watchdog_log():
    return {
        "student_id": "ST-002",
        "exam_id": "NEET-UG-2026",
        "center_id": "CTR-DELHI-12",
        "room_number": "Room 3",
        "keystroke_latency_ms": [10, 12, 11, 10, 11, 12],
        "focus_losses": 14,
        "gaze_deviation_count": 22
    }

@pytest.fixture
def sample_detective_log():
    return {
        "exam_id": "NEET-UG-2026",
        "total_candidates_analyzed": 1420,
        "flagged_center": "CTR-DELHI-12",
        "collusion_suspects": [
            {
                "room": "Room 3",
                "students": ["ST-002", "ST-003", "ST-004", "ST-008", "ST-011"],
                "identical_wrong_answers_count": 5,
                "shared_incorrect_choices": ["Q12", "Q15", "Q22"]
            }
        ]
    }

def test_models():
    incident = ExamIncident(
        incident_id="EXM-TEST-001",
        severity=SeverityLevel.CRITICAL,
        integrity_score=0.05,
        evidence_chain=["Test pre-exam breach detected"],
        audit_trail_hash="TEST_SIGNATURE",
        created_at=datetime.utcnow(),
        metadata_payload={}
    )
    assert incident.incident_id == "EXM-TEST-001"
    assert incident.severity == SeverityLevel.CRITICAL
    assert incident.integrity_score == 0.05

@pytest.mark.asyncio
async def test_vault_agent(sample_vault_log):
    res = await run_vault_agent(sample_vault_log, [])
    assert "suspicion_level" in res
    assert "anomalies_detected" in res
    assert "reasoning" in res

@pytest.mark.asyncio
async def test_watchdog_agent(sample_watchdog_log):
    res = await run_watchdog_agent(sample_watchdog_log, [])
    assert "confidence_score" in res
    assert "suspicion_level" in res
    assert "indicators" in res

@pytest.mark.asyncio
async def test_detective_agent(sample_detective_log):
    res = await run_detective_agent(sample_detective_log, [])
    assert "collusion_clusters" in res
    assert "suspicion_level" in res
    assert "reasoning" in res

@pytest.mark.asyncio
async def test_oracle_agent():
    vault_findings = {"suspicion_level": "CRITICAL"}
    watchdog_findings = [{"confidence_score": 0.95}]
    detective_findings = {"suspicion_level": "CRITICAL"}
    
    res = await run_oracle_agent(vault_findings, watchdog_findings, detective_findings)
    assert "final_severity" in res
    assert "evidence_chain" in res
    assert "correlated_findings" in res

def test_graph_compiles():
    assert app_graph is not None
