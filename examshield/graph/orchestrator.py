import uuid
import logging
from datetime import datetime
from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import StateGraph

from examshield.models.incident import ExamIncident, PhaseType, SeverityLevel
from examshield.models.agent_message import AgentStep, IncidentCreated, ResolutionComplete
from examshield.ws.manager import manager
from examshield.db.postgres import get_pool, insert_incident, update_incident_resolved
from examshield.db.chroma import get_similar_incidents, store_resolved_incident

from examshield.agents.vault_agent import run_vault_agent
from examshield.agents.watchdog_agent import run_watchdog_agent
from examshield.agents.detective_agent import run_detective_agent
from examshield.agents.oracle_agent import run_oracle_agent

logger = logging.getLogger(__name__)

def append_steps(left: list, right: list) -> list:
    return left + right

class ExamShieldState(TypedDict):
    # Inputs
    pre_exam_log: Dict[str, Any]
    student_session_log: Dict[str, Any]
    post_exam_data: Dict[str, Any]
    
    # State data
    incident: ExamIncident | None
    vault_findings: Dict[str, Any] | None
    watchdog_findings: Dict[str, Any] | None
    detective_findings: Dict[str, Any] | None
    oracle_findings: Dict[str, Any] | None
    
    # Audit trail & steps
    agent_steps: Annotated[list[AgentStep], append_steps]
    error: str | None

async def vault_node(state: ExamShieldState) -> dict:
    log_segment = state["pre_exam_log"]
    
    # Fetch similar cases from memory
    similar = get_similar_incidents(classification="unauthorized_access", location="vault", top_k=2)
    
    res = await run_vault_agent(log_segment, similar)
    
    # Broadcast step
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Vault",
        incident_id="",  # Will be assigned once Incident is created
        thought=res.get("reasoning", "Analyzing access logs..."),
        action=f"Scanned pre-exam logs. Suspicion: {res.get('suspicion_level', 'LOW')}",
        output=res,
        timestamp=datetime.utcnow(),
        is_final=False
    )
    await manager.broadcast(step.model_dump_json())
    
    return {
        "vault_findings": res,
        "agent_steps": [step]
    }

async def watchdog_node(state: ExamShieldState) -> dict:
    session_log = state["student_session_log"]
    
    similar = get_similar_incidents(classification="proctoring_violation", location="classroom", top_k=2)
    
    res = await run_watchdog_agent(session_log, similar)
    
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Watchdog",
        incident_id="",
        thought=res.get("reasoning", "Proctoring active session..."),
        action=f"Checked student session. Cheating confidence: {res.get('confidence_score', 0.0)}",
        output=res,
        timestamp=datetime.utcnow(),
        is_final=False
    )
    await manager.broadcast(step.model_dump_json())
    
    return {
        "watchdog_findings": res,
        "agent_steps": [step]
    }

async def detective_node(state: ExamShieldState) -> dict:
    post_data = state["post_exam_data"]
    
    similar = get_similar_incidents(classification="collusion_detection", location="statistics", top_k=2)
    
    res = await run_detective_agent(post_data, similar)
    
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Detective",
        incident_id="",
        thought=res.get("reasoning", "Auditing exam statistical answers..."),
        action=f"Identified {len(res.get('collusion_clusters', []))} collusion clusters and {len(res.get('leaked_questions', []))} leaked questions.",
        output=res,
        timestamp=datetime.utcnow(),
        is_final=False
    )
    await manager.broadcast(step.model_dump_json())
    
    return {
        "detective_findings": res,
        "agent_steps": [step]
    }

async def oracle_node(state: ExamShieldState) -> dict:
    vault = state.get("vault_findings") or {}
    watchdog = state.get("watchdog_findings") or {}
    detective = state.get("detective_findings") or {}
    
    res = await run_oracle_agent(vault, [watchdog], detective)
    
    # Create the Unified Exam Incident
    severity = SeverityLevel(res.get("final_severity", "LOW").lower())
    
    incident = ExamIncident(
        incident_id=f"EXM-{uuid.uuid4().hex[:8].upper()}",
        severity=severity,
        integrity_score=1.0 - watchdog.get("confidence_score", 0.0),
        evidence_chain=res.get("evidence_chain", []),
        audit_trail_hash=res.get("audit_trail_hash", "MOCK_SIG"),
        created_at=datetime.utcnow(),
        metadata_payload={
            "vault": vault,
            "watchdog": watchdog,
            "detective": detective
        }
    )
    
    # Insert incident into Postgres
    pool = get_pool()
    if pool:
        await insert_incident(pool, incident)
        
    # Broadcast Incident Created
    created_msg = IncidentCreated(
        message_type="incident_created",
        incident=incident
    )
    await manager.broadcast(created_msg.model_dump_json())
    
    # Broadcast Oracle Step
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Oracle",
        incident_id=incident.incident_id,
        thought=res.get("correlated_findings", "Generating final report..."),
        action=f"Compiled final dossier. Integrity status: {incident.severity.value.upper()}",
        output=res,
        timestamp=datetime.utcnow(),
        is_final=True
    )
    await manager.broadcast(step.model_dump_json())
    
    return {
        "incident": incident,
        "oracle_findings": res,
        "agent_steps": [step]
    }

async def finalizer_node(state: ExamShieldState) -> dict:
    inc = state["incident"]
    if not inc:
        return {}
        
    oracle = state.get("oracle_findings") or {}
    remediation_str = ", ".join(oracle.get("remediation_plan", []))
    summary = f"Audit complete for incident {inc.incident_id}. Findings correlated. Recommended action: {remediation_str}"
    
    inc.resolution_summary = summary
    inc.resolved_at = datetime.utcnow()
    
    pool = get_pool()
    if pool:
        await update_incident_resolved(pool, inc.incident_id, summary)
        
    # Store in Chroma memory
    store_resolved_incident(inc)
    
    # Broadcast Resolution Complete
    msg = ResolutionComplete(
        message_type="resolution_complete",
        incident_id=inc.incident_id,
        duration_seconds=(datetime.utcnow() - inc.created_at).total_seconds(),
        summary=summary
    )
    await manager.broadcast(msg.model_dump_json())
    
    return {}

# Define LangGraph flow
builder = StateGraph(ExamShieldState)

builder.add_node("vault", vault_node)
builder.add_node("watchdog", watchdog_node)
builder.add_node("detective", detective_node)
builder.add_node("oracle", oracle_node)
builder.add_node("finalizer", finalizer_node)

builder.set_entry_point("vault")
builder.add_edge("vault", "watchdog")
builder.add_edge("watchdog", "detective")
builder.add_edge("detective", "oracle")
builder.add_edge("oracle", "finalizer")
builder.set_finish_point("finalizer")

app_graph = builder.compile()
