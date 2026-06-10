import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from examshield.config import settings
from examshield.ws.manager import manager
from examshield.bus.redis_bus import start_sensor_listener
from examshield.db.postgres import create_pool, run_schema_migrations, get_recent_incidents, clear_database
from examshield.db.chroma import clear_chroma
from examshield.graph.orchestrator import app_graph, ExamShieldState
from examshield.models.agent_message import ErrorMessage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditPayload(BaseModel):
    pre_exam_log: Dict[str, Any]
    student_session_log: Dict[str, Any]
    post_exam_data: Dict[str, Any]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB Pool
    pool = await create_pool()
    app.state.pool = pool
    
    # Run Schema Migrations
    await run_schema_migrations(pool)
    
    # Start Redis Pub/Sub listener in the background
    redis_task = asyncio.create_task(start_sensor_listener(handle_audit_flow))
    
    yield
    
    # Clean up background listener
    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass
        
    # Close pool
    await pool.close()

app = FastAPI(
    title="ExamShield Autonomous Exam Integrity Engine",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "examshield-backend"}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        manager.disconnect(ws)

@app.get("/incidents")
async def list_incidents(request: Request):
    try:
        rows = await get_recent_incidents(request.app.state.pool, limit=20)
        return rows
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        return {"error": str(e)}

@app.post("/inject")
async def inject_audit(payload: AuditPayload):
    """
    Manually injects logs for audit analysis.
    This triggers the complete 3-phase ExamShield LangGraph pipeline.
    """
    asyncio.create_task(handle_audit_flow(
        payload.pre_exam_log,
        payload.student_session_log,
        payload.post_exam_data
    ))
    return {"status": "injected"}

@app.post("/reset")
async def reset_demo(request: Request):
    """
    Clears PostgreSQL and ChromaDB stores to reset the application state.
    """
    try:
        await clear_database(request.app.state.pool)
        clear_chroma()
        return {"status": "success", "detail": "ExamShield database and vector memory cleared."}
    except Exception as e:
        logger.error(f"Reset error: {e}")
        return {"status": "error", "detail": str(e)}

async def handle_audit_flow(pre_exam_log: dict, student_session_log: dict, post_exam_data: dict):
    """
    Executes the ExamShield LangGraph workflow on the given audit inputs.
    """
    initial_state = ExamShieldState(
        pre_exam_log=pre_exam_log,
        student_session_log=student_session_log,
        post_exam_data=post_exam_data,
        incident=None,
        vault_findings=None,
        watchdog_findings=None,
        detective_findings=None,
        oracle_findings=None,
        agent_steps=[],
        error=None
    )
    try:
        await app_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        err_msg = ErrorMessage(
            message_type="error",
            detail=f"ExamShield orchestrator failed: {str(e)}"
        )
        await manager.broadcast(err_msg.model_dump_json())
