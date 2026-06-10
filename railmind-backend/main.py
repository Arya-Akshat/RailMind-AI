import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware

from models.incident import SensorEvent
from models.agent_message import ErrorMessage
from ws.manager import manager
from bus.redis_bus import start_sensor_listener
from db.postgres import create_pool, run_schema_migrations, get_recent_incidents, clear_database
from db.chroma import clear_chroma
from graph.orchestrator import app_graph, RailMindState

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB Pool
    pool = await create_pool()
    app.state.pool = pool
    
    # Run Schema Migrations
    await run_schema_migrations(pool)
    
    # Start Redis Pub/Sub sensor listener task
    redis_task = asyncio.create_task(start_sensor_listener(handle_sensor_event))
    
    yield
    
    # Clean up Redis listener
    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass
        
    # Close DB Pool
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
        rows = await get_recent_incidents(request.app.state.pool, limit=20)
        return rows
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
        await clear_database(request.app.state.pool)
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
