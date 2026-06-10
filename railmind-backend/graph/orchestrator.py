import uuid
from datetime import datetime
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph

from models.incident import SensorEvent, Incident, SeverityLevel, WorkOrder, TrainReroute
from models.agent_message import AgentStep, IncidentCreated, ResolutionComplete
from ws.manager import manager
from db.postgres import (
    get_pool,
    insert_incident,
    update_incident_resolved,
    insert_work_order,
    insert_reroute
)
from db.chroma import get_similar_incidents, store_resolved_incident
from agents.sentinel import run_sentinel
from agents.commander import run_commander
from agents.dispatcher import run_dispatcher
from agents.scheduler import run_scheduler
from agents.communicator import run_communicator

def append_steps(left: list, right: list) -> list:
    return left + right

class RailMindState(TypedDict):
    sensor_event: SensorEvent
    incident: Incident | None
    commander_decision: dict | None
    work_order: WorkOrder | None
    reroutes: list[TrainReroute]
    alerts: dict | None
    agent_steps: Annotated[list[AgentStep], append_steps]
    error: str | None

async def sentinel_node(state: RailMindState) -> dict:
    event = state["sensor_event"]
    
    # 1. Query Chroma for similar past incidents
    similar = get_similar_incidents(classification=event.sensor_type, location=event.location, top_k=3)
    
    # 2. Run Sentinel agent
    try:
        res = await run_sentinel(event, similar)
        classification = res.get("classification", "vibration_anomaly")
        severity_str = res.get("severity", "medium")
        confidence = float(res.get("confidence", 0.5))
        reasoning = res.get("reasoning", "Sensor reading exceeded threshold.")
    except Exception as e:
        print(f"Sentinel node error: {e}")
        classification = "vibration_anomaly"
        severity_str = "medium"
        confidence = 0.5
        reasoning = f"Sentinel failed: {e}. Using fallback classification."
        
    severity = SeverityLevel(severity_str)
    
    # 3. Create Incident
    incident = Incident(
        incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
        sensor_event=event,
        severity=severity,
        classification=classification,
        confidence=confidence,
        created_at=datetime.utcnow()
    )
    
    # 4. Save to Postgres
    pool = get_pool()
    if pool:
        await insert_incident(pool, incident)
        
    # 5. Broadcast IncidentCreated
    created_msg = IncidentCreated(
        message_type="incident_created",
        incident=incident
    )
    await manager.broadcast(created_msg.model_dump_json())
    
    # 6. Create AgentStep & Broadcast
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Sentinel",
        incident_id=incident.incident_id,
        thought=reasoning,
        action=f"Classified as {classification} ({severity.value})",
        output={"classification": classification, "severity": severity.value, "confidence": confidence},
        timestamp=datetime.utcnow(),
        is_final=False
    )
    
    await manager.broadcast(step.model_dump_json())
    
    return {
        "incident": incident,
        "agent_steps": [step]
    }

async def commander_node(state: RailMindState) -> dict:
    inc = state["incident"]
    if not inc:
        return {}
        
    try:
        res = await run_commander(
            incident_id=inc.incident_id,
            classification=inc.classification,
            severity=inc.severity.value,
            confidence=inc.confidence,
            location=inc.sensor_event.location
        )
        reasoning = res.get("reasoning", "Evaluated incident severity and determined next steps.")
    except Exception as e:
        print(f"Commander node error: {e}")
        res = {
            "activate_dispatcher": True,
            "activate_scheduler": True,
            "activate_communicator": True,
            "priority": "standard",
            "reasoning": f"Commander failed: {e}. Falling back to full activation."
        }
        reasoning = res["reasoning"]
        
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Commander",
        incident_id=inc.incident_id,
        thought=reasoning,
        action=f"Response priority set to {res.get('priority', 'standard')}",
        output=res,
        timestamp=datetime.utcnow(),
        is_final=False
    )
    
    await manager.broadcast(step.model_dump_json())
    
    return {
        "commander_decision": res,
        "agent_steps": [step]
    }

async def dispatcher_node(state: RailMindState) -> dict:
    inc = state["incident"]
    decision = state["commander_decision"]
    if not inc or not decision:
        return {}
        
    priority = decision.get("priority", "standard")
    
    try:
        work_order, res = await run_dispatcher(
            incident_id=inc.incident_id,
            classification=inc.classification,
            severity=inc.severity.value,
            location=inc.sensor_event.location,
            priority=priority
        )
        reasoning = res.get("reasoning", f"Assigned crew {work_order.crew_id}.")
        action = res.get("work_order_summary", f"Dispatched {work_order.crew_id}")
    except Exception as e:
        print(f"Dispatcher node error: {e}")
        work_order = WorkOrder(
            work_order_id=f"WO-{uuid.uuid4().hex[:8].upper()}",
            incident_id=inc.incident_id,
            crew_id="CREW-FALLBACK",
            action="Inspect and repair",
            eta_minutes=60,
            created_at=datetime.utcnow()
        )
        reasoning = f"Dispatcher failed: {e}. Using fallback crew assignment."
        action = "Fallback dispatch crew assigned"
        res = {"crew_id": "CREW-FALLBACK", "action": "Inspect and repair", "eta_minutes": 60, "reasoning": reasoning}

    pool = get_pool()
    if pool:
        await insert_work_order(pool, work_order)
        
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Dispatcher",
        incident_id=inc.incident_id,
        thought=reasoning,
        action=action,
        output=res,
        timestamp=datetime.utcnow(),
        is_final=False
    )
    
    await manager.broadcast(step.model_dump_json())
    
    return {
        "work_order": work_order,
        "agent_steps": [step]
    }

async def scheduler_node(state: RailMindState) -> dict:
    inc = state["incident"]
    if not inc:
        return {}
        
    # Get ETA from work order if dispatched, default to 60 min
    eta = state["work_order"].eta_minutes if state.get("work_order") else 60
    
    try:
        reroutes, res = await run_scheduler(
            incident_id=inc.incident_id,
            location=inc.sensor_event.location,
            classification=inc.classification,
            eta_minutes=eta
        )
        reasoning = res.get("reasoning", "Analyzed routes for affected trains.")
    except Exception as e:
        print(f"Scheduler node error: {e}")
        reroutes = []
        reasoning = f"Scheduler failed: {e}. No reroutes computed."
        res = {"reroutes": [], "reasoning": reasoning}
        
    pool = get_pool()
    if pool:
        for r in reroutes:
            await insert_reroute(pool, inc.incident_id, r)
            
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Scheduler",
        incident_id=inc.incident_id,
        thought=reasoning,
        action=f"Computed reroutes for {len(reroutes)} trains",
        output=res,
        timestamp=datetime.utcnow(),
        is_final=False
    )
    
    await manager.broadcast(step.model_dump_json())
    
    return {
        "reroutes": reroutes,
        "agent_steps": [step]
    }

async def communicator_node(state: RailMindState) -> dict:
    inc = state["incident"]
    if not inc:
        return {}
        
    wo = state.get("work_order")
    crew_id = wo.crew_id if wo else "None"
    eta_minutes = wo.eta_minutes if wo else 0
    
    reroutes = state.get("reroutes", [])
    reroutes_str = ", ".join([f"Train {r.train_id} (delay: {r.delay_minutes}m)" for r in reroutes]) if reroutes else "None"
    affected_trains = ", ".join([r.train_id for r in reroutes]) if reroutes else "None"
    
    try:
        res = await run_communicator(
            incident_id=inc.incident_id,
            classification=inc.classification,
            location=inc.sensor_event.location,
            affected_trains=affected_trains,
            reroutes=reroutes_str,
            crew_id=crew_id,
            eta_minutes=eta_minutes
        )
        reasoning = "Drafted passenger and crew communications."
    except Exception as e:
        print(f"Communicator node error: {e}")
        res = {
            "passenger_sms": "Operational delay near location. Alternate routes scheduled.",
            "station_master_notification": "Incident reported. Check master logs.",
            "channels": ["SMS", "PA system"]
        }
        reasoning = f"Communicator failed: {e}."
        
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid.uuid4()),
        agent_name="Communicator",
        incident_id=inc.incident_id,
        thought=reasoning,
        action="Drafted passenger SMS and station master alerts",
        output=res,
        timestamp=datetime.utcnow(),
        is_final=True
    )
    
    await manager.broadcast(step.model_dump_json())
    
    return {
        "alerts": res,
        "agent_steps": [step]
    }

def build_resolution_summary(state: RailMindState) -> str:
    inc = state["incident"]
    if not inc:
        return "Incident resolution complete."
        
    wo = state.get("work_order")
    reroutes = state.get("reroutes", [])
    alerts = state.get("alerts")
    
    summary = f"Incident {inc.incident_id} ({inc.classification}) detected at {inc.sensor_event.location} with {inc.severity.value} severity. "
    if wo:
        summary += f"Dispatched {wo.crew_id} with an ETA of {wo.eta_minutes} minutes. "
    else:
        summary += "No crew dispatched. "
        
    if reroutes:
        summary += f"Rerouted {len(reroutes)} trains. "
    else:
        summary += "No trains affected. "
        
    if alerts:
        summary += f"Alert drafted: '{alerts.get('passenger_sms')}'."
        
    return summary

async def finalizer_node(state: RailMindState) -> dict:
    inc = state["incident"]
    if not inc:
        return {}
        
    summary = build_resolution_summary(state)
    inc.resolution_summary = summary
    inc.resolved_at = datetime.utcnow()
    
    pool = get_pool()
    if pool:
        await update_incident_resolved(pool, inc.incident_id, summary)
        
    store_resolved_incident(inc)
    
    msg = ResolutionComplete(
        message_type="resolution_complete",
        incident_id=inc.incident_id,
        duration_seconds=(datetime.utcnow() - inc.created_at).total_seconds(),
        summary=summary
    )
    
    await manager.broadcast(msg.model_dump_json())
    return {}

def route_after_commander(state: RailMindState) -> list[str]:
    d = state["commander_decision"]
    next_nodes = []
    if d:
        if d.get("activate_dispatcher"):
            next_nodes.append("dispatcher")
        if d.get("activate_scheduler"):
            next_nodes.append("scheduler")
        if d.get("activate_communicator"):
            next_nodes.append("communicator")
    
    return next_nodes if next_nodes else ["communicator"]

# Build state graph
builder = StateGraph(RailMindState)

builder.add_node("sentinel", sentinel_node)
builder.add_node("commander", commander_node)
builder.add_node("dispatcher", dispatcher_node)
builder.add_node("scheduler", scheduler_node)
builder.add_node("communicator", communicator_node)
builder.add_node("finalizer", finalizer_node)

builder.set_entry_point("sentinel")
builder.add_edge("sentinel", "commander")
builder.add_conditional_edges("commander", route_after_commander)
builder.add_edge("dispatcher", "finalizer")
builder.add_edge("scheduler", "finalizer")
builder.add_edge("communicator", "finalizer")
builder.set_finish_point("finalizer")

app_graph = builder.compile()
