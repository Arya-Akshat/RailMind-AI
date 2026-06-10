import asyncio
import json
import redis.asyncio
from config import settings
from models.incident import SensorEvent

async def start_sensor_listener(orchestrator_callback):
    r = redis.asyncio.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe("railmind:sensor_events")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    event = SensorEvent(**payload)
                    asyncio.create_task(orchestrator_callback(event))
                except Exception as e:
                    print(f"Error processing message from Redis: {e}")
    except Exception as e:
        print(f"Redis connection error in listener: {e}")
