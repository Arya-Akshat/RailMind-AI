import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware

from models.incident import SensorEvent
from models.agent_message import ErrorMessage
from ws.manager import manager
from bus.redis_bus import start_sensor_listener
from db.postgres import create_pool, run_schema_migrations, get_recent_incidents, clear_database, get_pool
from db.chroma import clear_chroma
from graph.orchestrator import app_graph, RailMindState

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB Pool — gracefully handle missing PostgreSQL
    pool = None
    try:
        pool = await create_pool()
        app.state.pool = pool
        await run_schema_migrations(pool)
        print("[OK] PostgreSQL connected and migrations applied.")
    except Exception as e:
        print(f"[WARN] PostgreSQL unavailable ({e}). Running in memory-only mode.")
        app.state.pool = None

    # Start Redis Pub/Sub sensor listener task — gracefully handle missing Redis
    redis_task = None
    try:
        redis_task = asyncio.create_task(start_sensor_listener(handle_sensor_event))
        # Give it a moment to connect; if it fails fast, we catch it
        await asyncio.sleep(0.5)
        if redis_task.done() and redis_task.exception():
            raise redis_task.exception()
        print("[OK] Redis sensor listener started.")
    except Exception as e:
        print(f"[WARN] Redis unavailable ({e}). Sensor injection via /inject endpoint only.")
        if redis_task and not redis_task.done():
            redis_task.cancel()
        redis_task = None

    yield

    # Clean up Redis listener
    if redis_task and not redis_task.done():
        redis_task.cancel()
        try:
            await redis_task
        except asyncio.CancelledError:
            pass

    # Close DB Pool
    if pool:
        await pool.close()

app = FastAPI(
    title="RailMind Autonomous Operations Backend",
    lifespan=lifespan
)

# Hackathon CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "railmind-backend"}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            # Keep-alive loop, clients may send ping text
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        manager.disconnect(ws)

@app.get("/incidents")
async def list_incidents(request: Request):
    try:
        pool = request.app.state.pool
        if pool:
            rows = await get_recent_incidents(pool, limit=20)
            return rows
        return []
    except Exception as e:
        return {"error": str(e)}

@app.post("/inject")
async def inject_event(event: SensorEvent):
    """
    Directly injects a SensorEvent scenario without requiring Redis pub/sub.
    Saves setup overhead for the frontend.
    """
    asyncio.create_task(handle_sensor_event(event))
    return {"status": "injected", "event_id": event.event_id}

@app.post("/reset")
async def reset_demo(request: Request):
    """
    Clears PostgreSQL database log and resets ChromaDB collections.
    Ensures a clean state for demo rehearsals.
    """
    try:
        pool = request.app.state.pool
        if pool:
            await clear_database(pool)
        clear_chroma()
        return {"status": "success", "detail": "Incident store and memory cleared successfully."}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

async def handle_sensor_event(event: SensorEvent):
    """
    Callback function that invokes the LangGraph orchestrator state machine.
    """
    initial_state = RailMindState(
        sensor_event=event,
        incident=None,
        commander_decision=None,
        work_order=None,
        reroutes=[],
        alerts=None,
        agent_steps=[],
        error=None
    )
    try:
        await app_graph.ainvoke(initial_state)
    except Exception as e:
        print(f"Error executing orchestrator graph: {e}")
        # Broadcast error to UI
        err_msg = ErrorMessage(
            message_type="error",
            detail=f"Resolution orchestrator pipeline crashed: {str(e)}"
        )
        await manager.broadcast(err_msg.model_dump_json())
