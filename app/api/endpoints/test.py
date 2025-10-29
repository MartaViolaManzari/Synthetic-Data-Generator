from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio, json

router = APIRouter()


@router.get("/")
async def say_hello():
    return {"message": "Hello, World!"}


@router.get("/progress")
async def test_progress():
    async def event_generator():
        for i, msg in [(10, "Preparazione..."),
                       (40, "Elaborazione..."),
                       (70, "Quasi finito..."),
                       (100, "Completato!")]:
            yield {"event": "message", "data": json.dumps({"progress": i, "message": msg})}
            await asyncio.sleep(1)  # simula tempo di lavoro

    return EventSourceResponse(event_generator())