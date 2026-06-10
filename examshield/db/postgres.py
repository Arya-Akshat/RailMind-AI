import json
from datetime import datetime
import asyncpg
from examshield.config import settings
from examshield.models.incident import ExamIncident

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
        CREATE TABLE IF NOT EXISTS exam_incidents (
            incident_id TEXT PRIMARY KEY,
            severity TEXT NOT NULL,
            integrity_score REAL NOT NULL,
            evidence_chain JSONB NOT NULL,
            audit_trail_hash TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL,
            resolved_at TIMESTAMPTZ,
            resolution_summary TEXT,
            metadata_payload JSONB
        );
        """)

async def insert_incident(pool, incident: ExamIncident):
    async with pool.acquire() as conn:
        evidence_json = json.dumps(incident.evidence_chain)
        meta_json = json.dumps(incident.metadata_payload)
        await conn.execute(
            """
            INSERT INTO exam_incidents (
                incident_id, severity, integrity_score, evidence_chain, audit_trail_hash, created_at, resolved_at, resolution_summary, metadata_payload
            ) VALUES ($1, $2, $3, CAST($4 AS jsonb), $5, $6, $7, $8, CAST($9 AS jsonb))
            ON CONFLICT (incident_id) DO NOTHING
            """,
            incident.incident_id,
            incident.severity.value,
            incident.integrity_score,
            evidence_json,
            incident.audit_trail_hash,
            incident.created_at,
            incident.resolved_at,
            incident.resolution_summary,
            meta_json
        )

async def update_incident_resolved(pool, incident_id: str, summary: str):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE exam_incidents
            SET resolved_at = $1, resolution_summary = $2
            WHERE incident_id = $3
            """,
            datetime.utcnow(),
            summary,
            incident_id
        )

async def get_recent_incidents(pool, limit=20) -> list[dict]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT incident_id, severity, integrity_score, evidence_chain, audit_trail_hash, created_at, resolved_at, resolution_summary, metadata_payload
            FROM exam_incidents
            ORDER BY created_at DESC
            LIMIT $1
            """,
            limit
        )
        result = []
        for r in rows:
            ev = r['evidence_chain']
            if isinstance(ev, str):
                ev = json.loads(ev)
            meta = r['metadata_payload']
            if isinstance(meta, str):
                meta = json.loads(meta)
            result.append({
                "incident_id": r["incident_id"],
                "severity": r["severity"],
                "integrity_score": r["integrity_score"],
                "evidence_chain": ev,
                "audit_trail_hash": r["audit_trail_hash"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "resolved_at": r["resolved_at"].isoformat() if r["resolved_at"] else None,
                "resolution_summary": r["resolution_summary"],
                "metadata_payload": meta
            })
        return result

async def clear_database(pool):
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE exam_incidents CASCADE;")
