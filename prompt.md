# RailMind — Person A: Backend Implementation Prompt

You are an expert Python backend engineer. Your task is to implement the complete backend for
**RailMind**, an autonomous multi-agent railway operations system. This is a hackathon project
built by a 2-person team. You own everything on the server side. The frontend (Next.js dashboard)
is built separately by Person B and will connect to your WebSocket endpoint.

---

## What you are building

RailMind detects railway incidents from a simulated sensor feed and resolves them autonomously
using a swarm of 5 AI agents orchestrated by LangGraph. Every agent decision streams in real time
to the frontend via WebSocket so judges can watch the reasoning unfold live.

---

## Tech stack

- **Python 3.11+**
- **FastAPI** — REST + WebSocket server
- **LangGraph** — stateful agent orchestration graph
- **Anthropic Python SDK** (`anthropic`) — Claude API calls inside each agent
- **Redis** — pub/sub bus between the sensor simulator and the orchestrator
- **PostgreSQL** — persistent storage for incidents and work orders
- **ChromaDB** — vector store for incident memory (similar past incidents)
- **Pydantic v2** — all data models
- **`python-dotenv`** — environment config
- **`asyncpg`** — async PostgreSQL driver
- **`redis.asyncio`** — async Redis client

---

## Project structure

```
railmind-backend/
├── main.py                  # FastAPI app entry point
├── .env                     # secrets (never commit)
├── requirements.txt
├── config.py                # settings loaded from .env
├── models/
│   ├── incident.py          # Pydantic models
│   └── agent_message.py     # WebSocket message shapes
├── db/
│   ├── postgres.py          # asyncpg pool + queries
│   └── chroma.py            # ChromaDB client + helpers
├── bus/
│   └── redis_bus.py         # Redis pub/sub subscriber
├── agents/
│   ├── base.py              # shared Claude call helper
│   ├── sentinel.py          # Agent 1
│   ├── commander.py         # Agent 2
│   ├── dispatcher.py        # Agent 3
│   ├── scheduler.py         # Agent 4
│   └── communicator.py      # Agent 5
├── graph/
│   └── orchestrator.py      # LangGraph state machine
└── ws/
    └── manager.py           # WebSocket connection manager
```

---

## Environment variables (`.env`)

```
ANTHROPIC_API_KEY=sk-ant-...
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://railmind:railmind@localhost:5432/railmind
CHROMA_PATH=./chroma_store
MODEL=claude-sonnet-4-20250514
```

---

## Data models (`models/`)

### `models/incident.py`

Define these Pydantic v2 models:

```python
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
```

### `models/agent_message.py`

This is the WebSocket contract that Person B's frontend will consume. Every message sent over
WebSocket must conform to this shape exactly. Agree on this with Person B on Day 1 and do not
change it without telling them.

```python
class AgentStep(BaseModel):
    message_type: Literal["agent_step"]
    step_id: str           # UUID
    agent_name: str        # "Sentinel" | "Commander" | "Dispatcher" | "Scheduler" | "Communicator"
    incident_id: str
    thought: str           # Claude's reasoning (stream this token by token if possible)
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
```

Send every message as `json.dumps(msg.model_dump(mode="json"))` over the WebSocket.

---

## WebSocket connection manager (`ws/manager.py`)

Implement a simple broadcast manager:

```python
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: str):
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)
```

---

## Redis pub/sub bus (`bus/redis_bus.py`)

Person B's sensor simulator publishes JSON to the Redis channel `railmind:sensor_events`.
Your subscriber listens on this channel and hands each event to the LangGraph orchestrator.

```python
async def start_sensor_listener(orchestrator_callback):
    r = redis.asyncio.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe("railmind:sensor_events")
    async for message in pubsub.listen():
        if message["type"] == "message":
            payload = json.loads(message["data"])
            event = SensorEvent(**payload)
            asyncio.create_task(orchestrator_callback(event))
```

Start this listener as a FastAPI `lifespan` background task, not in a route handler.

---

## PostgreSQL setup (`db/postgres.py`)

Create the pool on startup:

```python
async def create_pool():
    return await asyncpg.create_pool(settings.DATABASE_URL)
```

Schema (run once on startup with `CREATE TABLE IF NOT EXISTS`):

```sql
CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    sensor_event JSONB NOT NULL,
    severity TEXT NOT NULL,
    classification TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    resolution_summary TEXT
);

CREATE TABLE IF NOT EXISTS work_orders (
    work_order_id TEXT PRIMARY KEY,
    incident_id TEXT REFERENCES incidents(incident_id),
    crew_id TEXT NOT NULL,
    action TEXT NOT NULL,
    eta_minutes INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS train_reroutes (
    id SERIAL PRIMARY KEY,
    incident_id TEXT REFERENCES incidents(incident_id),
    train_id TEXT NOT NULL,
    original_route TEXT NOT NULL,
    new_route TEXT NOT NULL,
    delay_minutes INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Implement these async query functions:
- `insert_incident(pool, incident: Incident)`
- `update_incident_resolved(pool, incident_id, summary)`
- `insert_work_order(pool, work_order: WorkOrder)`
- `insert_reroute(pool, incident_id, reroute: TrainReroute)`
- `get_recent_incidents(pool, limit=20) -> list[dict]`

---

## ChromaDB setup (`db/chroma.py`)

Use the persistent client pointed at `settings.CHROMA_PATH`. Collection name: `incident_memory`.

Implement:

```python
def get_similar_incidents(classification: str, location: str, top_k=3) -> list[dict]:
    """
    Embed the query string f"{classification} at {location}" using ChromaDB's
    default embedding function (all-MiniLM-L6-v2 via sentence-transformers).
    Return the top_k most similar past incidents as dicts with keys:
    incident_id, classification, location, resolution_summary, distance.
    """

def store_resolved_incident(incident: Incident):
    """
    After resolution, upsert the incident into ChromaDB so future incidents
    can retrieve it as a reference. Document = resolution_summary.
    Metadata = {incident_id, classification, location, severity}.
    """
```

---

## The 5 agents (`agents/`)

### Shared helper (`agents/base.py`)

```python
async def call_claude(system: str, user: str, max_tokens=600) -> str:
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    msg = await client.messages.create(
        model=settings.MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    return msg.content[0].text
```

### Agent 1 — Sentinel (`agents/sentinel.py`)

Responsibility: Read the raw sensor event and classify the incident type and severity.

System prompt:
```
You are the Sentinel agent in RailMind, an autonomous railway operations system.
You receive raw sensor readings from trackside sensors and classify them into
structured incidents. You are precise, conservative, and always explain your
confidence level. When in doubt, escalate severity — false positives are
preferable to missed detections in a safety-critical system.
```

User prompt template:
```
A sensor event has been received. Classify this as a railway incident.

Sensor type: {sensor_type}
Location: {location}
Reading: {reading} (threshold: {threshold})
Raw payload: {raw_payload}

Similar past incidents for reference:
{similar_incidents}

Respond in this exact JSON format:
{{
  "classification": "<rail_fracture|signal_failure|track_obstruction|thermal_anomaly|vibration_anomaly>",
  "severity": "<low|medium|high|critical>",
  "confidence": <0.0-1.0>,
  "reasoning": "<your reasoning in 2-3 sentences>"
}}
```

Return: `(classification, severity, confidence, reasoning)`

### Agent 2 — Commander (`agents/commander.py`)

Responsibility: Receive the classified incident and decide the response strategy. Determines
which downstream agents to activate and in what priority order.

System prompt:
```
You are the Commander agent in RailMind. You receive classified incidents and
decide the tactical response. You know that Dispatcher handles crew deployment,
Scheduler handles train rerouting, and Communicator handles passenger alerts.
For critical incidents, activate all three. For high, activate Dispatcher and
Scheduler. For medium, activate Dispatcher only. For low, activate Communicator
only. Always state your reasoning clearly.
```

User prompt template:
```
Incident classified:
ID: {incident_id}
Classification: {classification}
Severity: {severity}
Confidence: {confidence}
Location: {location}

Decide the response strategy.

Respond in this exact JSON format:
{{
  "activate_dispatcher": true|false,
  "activate_scheduler": true|false,
  "activate_communicator": true|false,
  "priority": "<immediate|urgent|standard>",
  "reasoning": "<your reasoning in 2-3 sentences>"
}}
```

Return: `(activate_dispatcher, activate_scheduler, activate_communicator, priority, reasoning)`

### Agent 3 — Dispatcher (`agents/dispatcher.py`)

Responsibility: Assign the nearest available maintenance crew and create a work order.

System prompt:
```
You are the Dispatcher agent in RailMind. You assign maintenance crews to
incidents. You have access to a simulated crew registry. Choose the most
appropriate crew based on incident type and location. Create actionable
work orders with realistic ETAs based on Indian Railway geography.
```

User prompt template:
```
Incident requires crew dispatch:
ID: {incident_id}
Classification: {classification}
Severity: {severity}
Location: {location}
Priority: {priority}

Available crews (simulated):
- Crew ALPHA-7: Track maintenance specialists, currently at Mumbai Central (35 min from corridor)
- Crew BETA-3: Signal engineers, currently at Pune Junction (55 min from corridor)
- Crew GAMMA-1: Emergency response unit, currently at Surat depot (25 min from corridor)
- Crew DELTA-9: General maintenance, currently at Vadodara (45 min from corridor)

Assign a crew and create a work order.

Respond in this exact JSON format:
{{
  "crew_id": "<crew identifier>",
  "action": "<specific action the crew must take>",
  "eta_minutes": <integer>,
  "work_order_summary": "<one sentence summary>",
  "reasoning": "<your reasoning in 1-2 sentences>"
}}
```

Return: `WorkOrder` instance.

### Agent 4 — Scheduler (`agents/scheduler.py`)

Responsibility: Identify affected trains and compute reroutes to minimise network-wide delay.

System prompt:
```
You are the Scheduler agent in RailMind. You reroute trains away from
compromised track sections. You understand Indian Railway network topology.
Minimise total passenger delay across the network. Prefer diversions via
existing alternate routes over full cancellations. Always state the
delay impact clearly.
```

User prompt template:
```
Track section compromised:
Incident ID: {incident_id}
Location: {location}
Classification: {classification}
Estimated repair time: {eta_minutes} minutes

Affected trains (simulated):
- Train 12951 Rajdhani Express: Next stop affected section in 18 min
- Train 22119 Tejas Express: Next stop affected section in 34 min
- Train 19019 Saurashtra Mail: Next stop affected section in 52 min

Compute reroutes for all affected trains.

Respond in this exact JSON format:
{{
  "reroutes": [
    {{
      "train_id": "<train number>",
      "original_route": "<original route segment>",
      "new_route": "<alternate route>",
      "delay_minutes": <integer>,
      "reason": "<one sentence>"
    }}
  ],
  "total_passengers_affected": <integer estimate>,
  "reasoning": "<your reasoning in 2-3 sentences>"
}}
```

Return: `list[TrainReroute]`

### Agent 5 — Communicator (`agents/communicator.py`)

Responsibility: Draft passenger alerts and station master notifications.

System prompt:
```
You are the Communicator agent in RailMind. You draft clear, calm, and
accurate passenger-facing alerts and internal staff notifications. Passenger
messages must be non-alarming, factual, and include actionable guidance.
Staff notifications must be direct and include all operational details.
Write in both English and include a note that Hindi translation should follow.
```

User prompt template:
```
Incident resolved/in-progress, alerts required:
Incident ID: {incident_id}
Classification: {classification}
Location: {location}
Affected trains: {affected_trains}
Reroutes: {reroutes}
Crew dispatched: {crew_id}, ETA: {eta_minutes} min

Draft:
1. A passenger SMS alert (max 160 characters)
2. A station master notification (2-3 sentences, operational tone)

Respond in this exact JSON format:
{{
  "passenger_sms": "<max 160 chars>",
  "station_master_notification": "<2-3 sentences>",
  "channels": ["SMS", "PA system", "station display boards"]
}}
```

Return: `(passenger_sms, station_master_notification, channels)`

---

## LangGraph orchestrator (`graph/orchestrator.py`)

### State definition

```python
class RailMindState(TypedDict):
    sensor_event: SensorEvent
    incident: Incident | None
    commander_decision: dict | None
    work_order: WorkOrder | None
    reroutes: list[TrainReroute]
    alerts: dict | None
    agent_steps: list[AgentStep]
    error: str | None
```

### Graph nodes

Define one async node per agent. Each node must:
1. Call its agent function to get a result.
2. Append an `AgentStep` to `state["agent_steps"]`.
3. Broadcast the `AgentStep` over WebSocket immediately (do not wait for the full pipeline).
4. Return the updated state slice.

```python
async def sentinel_node(state: RailMindState) -> dict:
    ...
    step = AgentStep(
        message_type="agent_step",
        step_id=str(uuid4()),
        agent_name="Sentinel",
        incident_id=state["incident"].incident_id,
        thought=reasoning,
        action=f"Classified as {classification} ({severity})",
        output={"classification": classification, "severity": severity, "confidence": confidence},
        timestamp=datetime.utcnow(),
        is_final=False
    )
    state["agent_steps"].append(step)
    await manager.broadcast(step.model_dump_json())
    return {"incident": incident}
```

Repeat this pattern for all 5 nodes.

### Conditional routing

After the Commander node, use a conditional edge to decide which downstream agents to activate:

```python
def route_after_commander(state: RailMindState) -> list[str]:
    d = state["commander_decision"]
    next_nodes = []
    if d["activate_dispatcher"]:
        next_nodes.append("dispatcher")
    if d["activate_scheduler"]:
        next_nodes.append("scheduler")
    if d["activate_communicator"]:
        next_nodes.append("communicator")
    return next_nodes if next_nodes else ["communicator"]
```

### Graph construction

```python
graph = StateGraph(RailMindState)
graph.add_node("sentinel", sentinel_node)
graph.add_node("commander", commander_node)
graph.add_node("dispatcher", dispatcher_node)
graph.add_node("scheduler", scheduler_node)
graph.add_node("communicator", communicator_node)
graph.add_node("finalizer", finalizer_node)

graph.set_entry_point("sentinel")
graph.add_edge("sentinel", "commander")
graph.add_conditional_edges("commander", route_after_commander)
graph.add_edge("dispatcher", "finalizer")
graph.add_edge("scheduler", "finalizer")
graph.add_edge("communicator", "finalizer")
graph.set_finish_point("finalizer")

app_graph = graph.compile()
```

### Finalizer node

The finalizer runs after all downstream agents complete. It:
1. Marks the incident as resolved in PostgreSQL.
2. Stores the resolved incident in ChromaDB.
3. Broadcasts a `ResolutionComplete` message over WebSocket.

```python
async def finalizer_node(state: RailMindState) -> dict:
    summary = build_resolution_summary(state)
    await update_incident_resolved(pool, state["incident"].incident_id, summary)
    store_resolved_incident(state["incident"])
    msg = ResolutionComplete(
        message_type="resolution_complete",
        incident_id=state["incident"].incident_id,
        duration_seconds=(datetime.utcnow() - state["incident"].created_at).total_seconds(),
        summary=summary
    )
    await manager.broadcast(msg.model_dump_json())
    return {}
```

---

## FastAPI app (`main.py`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()
    await run_schema_migrations(app.state.pool)
    asyncio.create_task(start_sensor_listener(handle_sensor_event))
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()   # keep alive; frontend may send pings
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.get("/incidents")
async def list_incidents(request: Request):
    rows = await get_recent_incidents(request.app.state.pool)
    return rows

@app.post("/inject")
async def inject_event(event: SensorEvent):
    """
    Demo control endpoint. Person B's demo panel POSTs here to inject
    a scenario event without going through Redis. Identical to the
    Redis listener path — calls handle_sensor_event directly.
    """
    asyncio.create_task(handle_sensor_event(event))
    return {"status": "injected", "event_id": event.event_id}

async def handle_sensor_event(event: SensorEvent):
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
    await app_graph.ainvoke(initial_state)
```

---

## `requirements.txt`

```
fastapi
uvicorn[standard]
langgraph
anthropic
redis[asyncio]
asyncpg
chromadb
pydantic>=2.0
python-dotenv
sentence-transformers
```

---

## Day-by-day build order

### Day 1
- Set up the project structure and `.env`.
- Get FastAPI running with a `/health` endpoint.
- Implement the WebSocket manager and confirm Person B can connect.
- Stand up Redis locally and verify pub/sub works with a test publisher.
- Agree on the `AgentStep` JSON schema with Person B — do not change this after Day 1.

### Day 2
- Implement `SensorEvent` and `Incident` models.
- Build the Sentinel agent. Test it standalone with a hardcoded sensor event.
- Build the Commander agent. Test the routing logic.
- Wire both into a 2-node LangGraph graph and confirm state flows correctly.

### Day 3
- Build Dispatcher and Scheduler agents. Test each standalone.
- Add conditional routing after Commander.
- Run the full Sentinel → Commander → Dispatcher + Scheduler pipeline end-to-end.
- Each agent step should broadcast over WebSocket — confirm with a `wscat` client.

### Day 4
- Build Communicator agent.
- Build the Finalizer node.
- Add ChromaDB: implement `store_resolved_incident` and `get_similar_incidents`.
- Pass similar incidents into the Sentinel prompt and verify richer reasoning.

### Day 5
- Add PostgreSQL: create schema, implement all query functions.
- Implement the `/inject` REST endpoint for Person B's demo control panel.
- Implement the `/incidents` endpoint.
- Run a full end-to-end scenario from `POST /inject` → all 5 agents → `ResolutionComplete` WS message.
- Fix any agent prompt issues that produce malformed JSON (add a `try/except` + retry with a correction prompt).

### Day 6
- Integration session with Person B: connect the real frontend, fix any WebSocket or CORS issues.
- Rehearse the full demo scenario 3 times. Time it — target under 60 seconds from inject to resolution.
- Add a `/reset` endpoint that clears the incident log for a clean demo restart.
- Polish agent prompts for better reasoning text (this is what judges read on the thought chain panel).

---

## Demo scenarios (for `/inject`)

Prepare these 3 pre-built `SensorEvent` payloads that Person B's demo panel will fire:

### Scenario 1 — Critical rail fracture (the primary demo)
```json
{
  "event_id": "EVT-001",
  "timestamp": "<now>",
  "sensor_type": "vibration",
  "location": "Section 47B, Delhi-Mumbai Western Corridor",
  "reading": 9.4,
  "threshold": 6.0,
  "raw_payload": {
    "frequency_hz": 142,
    "amplitude_mm": 9.4,
    "duration_ms": 830,
    "sensor_id": "TRK-47B-VIB-03",
    "battery_pct": 87
  }
}
```

### Scenario 2 — Signal failure
```json
{
  "event_id": "EVT-002",
  "timestamp": "<now>",
  "sensor_type": "signal_health",
  "location": "Surat Signal Box, Section 22A",
  "reading": 0.0,
  "threshold": 1.0,
  "raw_payload": {
    "signal_id": "SIG-22A-04",
    "last_healthy_ping": "<5 min ago>",
    "failure_code": "NO_CARRIER",
    "affected_tracks": ["Up Main", "Down Main"]
  }
}
```

### Scenario 3 — Thermal anomaly (bridge bearing)
```json
{
  "event_id": "EVT-003",
  "timestamp": "<now>",
  "sensor_type": "thermal",
  "location": "Narmada Bridge, Section 31C",
  "reading": 87.3,
  "threshold": 65.0,
  "raw_payload": {
    "sensor_id": "BRG-31C-THERM-01",
    "ambient_temp_c": 38,
    "bearing_temp_c": 87.3,
    "wind_speed_kmh": 12
  }
}
```

---

## Important implementation notes

**JSON reliability:** Claude sometimes returns malformed JSON. Wrap every `call_claude` response
in a `try/except json.JSONDecodeError`. On failure, retry once with an appended instruction:
`"Your previous response was not valid JSON. Return only the JSON object with no additional text."`

**Parallel agent execution:** LangGraph supports fan-out natively. When Commander activates
Dispatcher, Scheduler, and Communicator simultaneously, they run in parallel via `asyncio`.
The Finalizer uses `add_edge` from all three, so LangGraph waits for all before proceeding.
Do not manually `asyncio.gather` — let the graph handle it.

**WebSocket broadcast timing:** Broadcast each `AgentStep` the moment the agent completes,
not after the whole graph finishes. This is what creates the live "thinking" effect on the
frontend. If you batch-send at the end, the demo loses its wow factor.

**ChromaDB on Day 1:** Do not block Day 1 on ChromaDB. Use an empty list for `similar_incidents`
in Sentinel's prompt until Day 4. The agent works without memory; it just reasons from scratch.

**Agent prompt max_tokens:** Keep each agent under 600 tokens output. Judges read the thought
chain — dense walls of text are worse than concise, confident reasoning.

**CORS:** Set `allow_origins=["*"]` for the hackathon. Do not spend time on auth.

**Error handling:** If any agent fails after 2 retries, broadcast an `ErrorMessage` over
WebSocket and continue the pipeline with a fallback response. Never let one agent failure
crash the whole incident resolution chain.