import asyncio
import json
from random import randint
from typing import Any, cast

from fastapi import APIRouter, Request
from fastapi.sse import EventSourceResponse

from collections.abc import AsyncIterable

from pydantic import BaseModel

from app.models.datastructs import StateModel

router = APIRouter()


class test(BaseModel):
    num: int


@router.get("/stream/dashboard", response_class=EventSourceResponse)
async def dashboardStream(request: Request):
    state = cast(StateModel, request.app.state)
    # now that we have a new connection, we add it to our internal array
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    state.adminStream.addAdmin("dashboard", queue)

    try:
        while True:
            msg = await queue.get()
            print(msg)
            queue.task_done()
            yield f"data: {json.dumps(msg)}\n\n"
    except asyncio.CancelledError:
        pass


@router.get("/stream/{roomID}")
async def roomStream(roomID: int):
    pass
