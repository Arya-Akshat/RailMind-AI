import json
from datetime import datetime
import asyncpg
from config import settings
from models.incident import Incident, WorkOrder, TrainReroute

_pool = None

async def create_pool():
    global _pool
    _pool = await asyncpg.create_pool(settings.DATABASE_URL)
    return _pool

def get_pool():
    return _pool

async def run_schema_migrations(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
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
            incident_id TEXT REFERENCES incidents(incident_id) ON DELETE CASCADE,
            crew_id TEXT NOT NULL,
            action TEXT NOT NULL,
            eta_minutes INTEGER NOT NULL,
            created_at TIMESTAMPTZ NOT NULL
        );

        CREATE TABLE IF NOT EXISTS train_reroutes (
            id SERIAL PRIMARY KEY,
            incident_id TEXT REFERENCES incidents(incident_id) ON DELETE CASCADE,
            train_id TEXT NOT NULL,
            original_route TEXT NOT NULL,
            new_route TEXT NOT NULL,
            delay_minutes INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)

async def insert_incident(pool, incident: Incident):
    if pool is None:
        return
    async with pool.acquire() as conn:
        # Convert SensorEvent to dict or JSON string to insert as JSONB.
        # asyncpg auto-serializes dicts to jsonb if encoder is set, but to be safe we can use JSON string and cast.
        event_json = json.dumps(incident.sensor_event.model_dump(mode="json"))
        await conn.execute(
            """
            INSERT INTO incidents (
                incident_id, sensor_event, severity, classification, confidence, created_at, resolved_at, resolution_summary
            ) VALUES ($1, CAST($2 AS jsonb), $3, $4, $5, $6, $7, $8)
            ON CONFLICT (incident_id) DO NOTHING
            """,
            incident.incident_id,
            event_json,
            incident.severity.value,
            incident.classification,
            incident.confidence,
            incident.created_at,
            incident.resolved_at,
            incident.resolution_summary
        )

async def update_incident_resolved(pool, incident_id: str, summary: str):
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE incidents
            SET resolved_at = $1, resolution_summary = $2
            WHERE incident_id = $3
            """,
            datetime.utcnow(),
            summary,
            incident_id
        )

async def insert_work_order(pool, work_order: WorkOrder):
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO work_orders (
                work_order_id, incident_id, crew_id, action, eta_minutes, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (work_order_id) DO NOTHING
            """,
            work_order.work_order_id,
            work_order.incident_id,
            work_order.crew_id,
            work_order.action,
            work_order.eta_minutes,
            work_order.created_at
        )

async def insert_reroute(pool, incident_id: str, reroute: TrainReroute):
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO train_reroutes (
                incident_id, train_id, original_route, new_route, delay_minutes, reason
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
            incident_id,
            reroute.train_id,
            reroute.original_route,
            reroute.new_route,
            reroute.delay_minutes,
            reroute.reason
        )

async def get_recent_incidents(pool, limit=20) -> list[dict]:
    if pool is None:
        return []
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT incident_id, sensor_event, severity, classification, confidence, created_at, resolved_at, resolution_summary
            FROM incidents
            ORDER BY created_at DESC
            LIMIT $1
            """,
            limit
        )
        result = []
        for r in rows:
            evt = r['sensor_event']
            if isinstance(evt, str):
                evt = json.loads(evt)
            result.append({
                "incident_id": r["incident_id"],
                "sensor_event": evt,
                "severity": r["severity"],
                "classification": r["classification"],
                "confidence": r["confidence"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "resolved_at": r["resolved_at"].isoformat() if r["resolved_at"] else None,
                "resolution_summary": r["resolution_summary"]
            })
        return result

async def clear_database(pool):
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE incidents CASCADE;")
