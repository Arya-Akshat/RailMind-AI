import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.incident import SensorEvent, Incident, SeverityLevel, WorkOrder, TrainReroute
from agents.sentinel import run_sentinel
from agents.commander import run_commander
from agents.dispatcher import run_dispatcher
from agents.scheduler import run_scheduler
from agents.communicator import run_communicator
from graph.orchestrator import app_graph, RailMindState, route_after_commander

@pytest.fixture
def sample_sensor_event():
    return SensorEvent(
        event_id="EVT-TEST-001",
        timestamp=datetime.utcnow(),
        sensor_type="vibration",
        location="Section 47B, Delhi-Mumbai Western Corridor",
        reading=9.4,
        threshold=6.0,
        raw_payload={
            "frequency_hz": 142,
            "amplitude_mm": 9.4,
            "duration_ms": 830
        }
    )

def test_models(sample_sensor_event):
    assert sample_sensor_event.event_id == "EVT-TEST-001"
    assert sample_sensor_event.reading == 9.4
    
    incident = Incident(
        incident_id="INC-TEST-001",
        sensor_event=sample_sensor_event,
        severity=SeverityLevel.CRITICAL,
        classification="rail_fracture",
        confidence=0.95,
        created_at=datetime.utcnow()
    )
    assert incident.incident_id == "INC-TEST-001"
    assert incident.severity == SeverityLevel.CRITICAL

@pytest.mark.asyncio
async def test_sentinel_agent(sample_sensor_event):
    res = await run_sentinel(sample_sensor_event, [])
    assert "classification" in res
    assert "severity" in res
    assert "confidence" in res
    assert "reasoning" in res

@pytest.mark.asyncio
async def test_commander_agent():
    res = await run_commander(
        incident_id="INC-TEST-001",
        classification="rail_fracture",
        severity="critical",
        confidence=0.95,
        location="Section 47B"
    )
    assert "activate_dispatcher" in res
    assert "activate_scheduler" in res
    assert "activate_communicator" in res
    assert res["activate_dispatcher"] is True

@pytest.mark.asyncio
async def test_dispatcher_agent():
    work_order, res = await run_dispatcher(
        incident_id="INC-TEST-001",
        classification="rail_fracture",
        severity="critical",
        location="Section 47B",
        priority="immediate"
    )
    assert isinstance(work_order, WorkOrder)
    assert work_order.incident_id == "INC-TEST-001"
    assert "crew_id" in res

@pytest.mark.asyncio
async def test_scheduler_agent():
    reroutes, res = await run_scheduler(
        incident_id="INC-TEST-001",
        location="Section 47B",
        classification="rail_fracture",
        eta_minutes=25
    )
    assert isinstance(reroutes, list)
    assert len(reroutes) > 0
    assert isinstance(reroutes[0], TrainReroute)

@pytest.mark.asyncio
async def test_communicator_agent():
    res = await run_communicator(
        incident_id="INC-TEST-001",
        classification="rail_fracture",
        location="Section 47B",
        crew_id="Crew GAMMA-1",
        eta_minutes=25
    )
    assert "passenger_sms" in res
    assert "station_master_notification" in res

def test_routing_logic():
    # Test routing after commander
    state_low = {
        "commander_decision": {
            "activate_dispatcher": False,
            "activate_scheduler": False,
            "activate_communicator": True,
            "priority": "standard"
        }
    }
    assert route_after_commander(state_low) == ["communicator"]

    state_med = {
        "commander_decision": {
            "activate_dispatcher": True,
            "activate_scheduler": False,
            "activate_communicator": False,
            "priority": "standard"
        }
    }
    assert route_after_commander(state_med) == ["dispatcher"]

    state_high = {
        "commander_decision": {
            "activate_dispatcher": True,
            "activate_scheduler": True,
            "activate_communicator": False,
            "priority": "urgent"
        }
    }
    assert "dispatcher" in route_after_commander(state_high)
    assert "scheduler" in route_after_commander(state_high)

    state_critical = {
        "commander_decision": {
            "activate_dispatcher": True,
            "activate_scheduler": True,
            "activate_communicator": True,
            "priority": "immediate"
        }
    }
    routes = route_after_commander(state_critical)
    assert "dispatcher" in routes
    assert "scheduler" in routes
    assert "communicator" in routes

def test_graph_compiles():
    assert app_graph is not None
