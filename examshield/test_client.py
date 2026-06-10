import asyncio
import websockets
import httpx
import json

INJECT_URL = "http://localhost:8000/inject"
WS_URL = "ws://localhost:8000/ws"

LEAK_SCENARIO = {
    "pre_exam_log": {
        "event_id": "PR-0491",
        "timestamp": "2026-06-10T02:15:22Z",
        "user_id": "USR-OFFICER-DEV",
        "role": "Exam Custodian",
        "ip_address": "203.0.113.15",
        "location": "Delhi Main Vault Server",
        "action": "DECRYPT_AND_DOWNLOAD",
        "download_size_gb": 4.2,
        "key_id": "KEY-NEET-UG-SET-B"
    },
    "student_session_log": {
        "student_id": "ST-002",
        "exam_id": "NEET-UG-2026",
        "center_id": "CTR-DELHI-12",
        "room_number": "Room 3",
        "keystroke_latency_ms": [10, 12, 11, 10, 11, 12],
        "focus_losses": 14,
        "gaze_deviation_count": 22,
        "anomalous_response_intervals": [
            {"question_id": "Q47", "time_seconds": 6},
            {"question_id": "Q48", "time_seconds": 8},
            {"question_id": "Q49", "time_seconds": 5},
            {"question_id": "Q50", "time_seconds": 7}
        ]
    },
    "post_exam_data": {
        "exam_id": "NEET-UG-2026",
        "total_candidates_analyzed": 1420,
        "flagged_center": "CTR-DELHI-12",
        "aberrant_statistics": [
            {
                "question_id": "Q47",
                "global_correct_rate": 0.38,
                "center_correct_rate": 0.96,
                "average_time_spent_seconds": 7.2
            },
            {
                "question_id": "Q48",
                "global_correct_rate": 0.42,
                "center_correct_rate": 0.94,
                "average_time_spent_seconds": 8.0
            }
        ],
        "collusion_suspects": [
            {
                "room": "Room 3",
                "students": ["ST-002", "ST-003", "ST-004", "ST-008", "ST-011"],
                "identical_wrong_answers_count": 5,
                "shared_incorrect_choices": ["Q12", "Q15", "Q22"]
            }
        ]
    }
}

async def listen_ws():
    try:
        async with websockets.connect(WS_URL) as ws:
            print("Connected to ExamShield WebSocket server.")
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                mtype = data.get("message_type")
                if mtype == "agent_step":
                    print(f"\n[{data['agent_name']} Agent Step]")
                    print(f"Thought: {data['thought']}")
                    print(f"Action: {data['action']}")
                elif mtype == "incident_created":
                    inc = data.get("incident", {})
                    print(f"\n[Incident Created] ID: {inc.get('incident_id')}")
                    print(f"Severity: {inc.get('severity')}")
                    print(f"Integrity Score: {inc.get('integrity_score')}")
                elif mtype == "resolution_complete":
                    print(f"\n[Resolution Complete]")
                    print(f"Summary: {data['summary']}")
                    print(f"Duration: {data['duration_seconds']}s")
                    break
    except Exception as e:
        print(f"WebSocket listener error: {e}")

async def main():
    # Start WS listener task
    listener = asyncio.create_task(listen_ws())
    
    # Wait for connection to establish
    await asyncio.sleep(1)
    
    # POST payload to /inject
    async with httpx.AsyncClient() as client:
        print("Injecting exam leak scenario...")
        r = await client.post(INJECT_URL, json=LEAK_SCENARIO)
        print(f"Injection status: {r.status_code} - {r.json()}")
        
    # Wait for the listener to complete
    await listener

if __name__ == "__main__":
    asyncio.run(main())
