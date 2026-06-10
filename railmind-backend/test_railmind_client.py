import asyncio
import websockets
import httpx
import json
import asyncpg
import chromadb
from datetime import datetime

INJECT_URL = "http://localhost:8000/inject"
WS_URL = "ws://localhost:8000/ws"
DB_URL = "postgresql://railmind:railmind@localhost:5432/railmind"
CHROMA_PATH = "./chroma_store"

SCENARIO_1 = {
    "event_id": "EVT-001",
    "timestamp": "2026-06-10T12:00:00Z",
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

SCENARIO_2 = {
    "event_id": "EVT-002",
    "timestamp": "2026-06-10T12:00:00Z",
    "sensor_type": "signal_health",
    "location": "Surat Signal Box, Section 22A",
    "reading": 0.0,
    "threshold": 1.0,
    "raw_payload": {
        "signal_id": "SIG-22A-04",
        "last_healthy_ping": "5 min ago",
        "failure_code": "NO_CARRIER",
        "affected_tracks": ["Up Main", "Down Main"]
    }
}

SCENARIO_3 = {
    "event_id": "EVT-003",
    "timestamp": "2026-06-10T12:00:00Z",
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

async def run_scenario(ws, scenario, label):
    print(f"\n--- Injecting {label} ---")
    
    # Inject scenario event
    async with httpx.AsyncClient() as client:
        r = await client.post(INJECT_URL, json=scenario)
        print(f"Injection status: {r.status_code} - {r.json()}")
        
    # Listen to WebSocket stream until ResolutionComplete or Timeout
    incident_id = None
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
            data = json.loads(msg)
            mtype = data.get("message_type")
            
            if mtype == "agent_step":
                print(f"[{data['agent_name']} Step] {data['action']}")
                print(f"  Thought: {data['thought']}")
                
            elif mtype == "incident_created":
                incident_id = data["incident"]["incident_id"]
                print(f"[Incident Created] ID: {incident_id}")
                
            elif mtype == "resolution_complete":
                print(f"[Resolution Complete] Summary: {data['summary']}")
                break
        except asyncio.TimeoutError:
            print("Timeout waiting for WebSocket messages.")
            break
            
    return incident_id

async def verify_db_records(conn, incident_id):
    print(f"\n--- Verifying PostgreSQL Records for Incident {incident_id} ---")
    
    # 1. Verify incident row
    inc_row = await conn.fetchrow("SELECT * FROM incidents WHERE incident_id = $1", incident_id)
    if inc_row:
        print(f"[SUCCESS] Incident Row: ID={inc_row['incident_id']}, Severity={inc_row['severity']}, Classification={inc_row['classification']}")
    else:
        print("[FAILED] Incident Row not found!")
        
    # 2. Verify work order row
    wo_row = await conn.fetchrow("SELECT * FROM work_orders WHERE incident_id = $1", incident_id)
    if wo_row:
        print(f"[SUCCESS] Work Order Row: ID={wo_row['work_order_id']}, Crew={wo_row['crew_id']}, Action={wo_row['action']}")
    else:
        print("[INFO] Work Order Row not found (expected if not activated by Commander).")
        
    # 3. Verify train reroutes
    route_rows = await conn.fetch("SELECT * FROM train_reroutes WHERE incident_id = $1", incident_id)
    if route_rows:
        print(f"[SUCCESS] Found {len(route_rows)} Train Reroute Row(s):")
        for r in route_rows:
            print(f"  Train={r['train_id']}, New Route={r['new_route']}, Delay={r['delay_minutes']}m")
    else:
        print("[INFO] Train Reroute Rows not found (expected if not activated by Commander).")

def verify_chroma(incident_id):
    print(f"\n--- Verifying ChromaDB Storage for Incident {incident_id} ---")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    col = client.get_collection("incident_memory")
    
    # Verify count
    print(f"Total documents in Chroma collection: {col.count()}")
    
    # Query for the specific incident
    results = col.get(ids=[incident_id])
    if results and len(results["ids"]) > 0:
        print(f"[SUCCESS] Incident found in Chroma. Summary: {results['documents'][0]}")
    else:
        print("[FAILED] Incident not found in Chroma by ID!")
        
    # Test similarity retrieval
    print("\nTesting Similarity Retrieval from Chroma...")
    similar = col.query(query_texts=["rail fracture at Section 47B"], n_results=1)
    if similar and len(similar["ids"]) > 0 and len(similar["ids"][0]) > 0:
        print(f"[SUCCESS] Retrieved similar case ID: {similar['ids'][0][0]}")
        print(f"  Document: {similar['documents'][0][0]}")
    else:
        print("[FAILED] Similarity query returned no results!")

async def main():
    # Connect to PostgreSQL
    conn = await asyncpg.connect(DB_URL)
    
    # Clean previous demo runs for clean validation
    print("Resetting database before test...")
    async with httpx.AsyncClient() as client:
        await client.post("http://localhost:8000/reset")
        
    # Connect to WebSocket
    async with websockets.connect(WS_URL) as ws:
        print("Connected to WebSocket successfully.")
        
        # Scenario 1
        inc1 = await run_scenario(ws, SCENARIO_1, "Scenario 1: Critical Rail Fracture")
        if inc1:
            await verify_db_records(conn, inc1)
            verify_chroma(inc1)
            
        # Scenario 2
        inc2 = await run_scenario(ws, SCENARIO_2, "Scenario 2: Signal Failure")
        if inc2:
            await verify_db_records(conn, inc2)
            
        # Scenario 3
        inc3 = await run_scenario(ws, SCENARIO_3, "Scenario 3: Thermal Anomaly")
        if inc3:
            await verify_db_records(conn, inc3)

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
