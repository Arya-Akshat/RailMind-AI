import asyncio
import json
import redis.asyncio
from examshield.config import settings

async def start_sensor_listener(orchestrator_callback):
    r = redis.asyncio.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe("examshield:audit_events")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    pre = payload.get("pre_exam_log", {})
                    stud = payload.get("student_session_log", {})
                    post = payload.get("post_exam_data", {})
                    asyncio.create_task(orchestrator_callback(pre, stud, post))
                except Exception as e:
                    print(f"Error processing message from Redis: {e}")
    except Exception as e:
        print(f"Redis connection error in listener: {e}")
