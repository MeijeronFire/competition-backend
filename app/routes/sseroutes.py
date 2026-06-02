# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
import json
import logging
from random import randint
from typing import Any, cast

from fastapi import APIRouter, Request
from fastapi.sse import EventSourceResponse

from collections.abc import AsyncIterable

from pydantic import BaseModel

from app.models.datastructs import StateModel

router = APIRouter()
logger = logging.getLogger(__name__)


class test(BaseModel):
    num: int


@router.get("/stream/dashboard", response_class=EventSourceResponse)
async def dashboardStream(request: Request):
    state = cast(StateModel, request.app.state)
    # now that we have a new connection, we add it to our internal array
    logger.info("new SSE connection")
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    state.adminStream.addAdmin("dashboard", queue)

    try:
        while True:
            # end connection at disconnect
            if await request.is_disconnected():
                break

            # timeout for stale connections
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=1)
            except asyncio.TimeoutError:
                continue

            # handle message sending
            # queue.task_done()
            yield {"data": json.dumps(msg)}
    finally:
        # disconnection hook
        state.adminStream.popAdmin("dashboard", queue)


@router.get("/stream/{roomID}")
async def roomStream(request: Request, roomID: int):
    state = cast(StateModel, request.app.state)
    # now that we have a new connection, we add it to our internal array
    logger.info(f"new SSE connection @{roomID}")
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    state.adminStream.addAdmin(f"room-{roomID}", queue)

    try:
        while True:
            # end connection at disconnect
            if await request.is_disconnected():
                break

            # timeout for stale connections
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=1)
            except asyncio.TimeoutError:
                continue

            # handle message sending
            # queue.task_done()
            yield {"data": json.dumps(msg)}
    finally:
        # disconnection hook
        state.adminStream.popAdmin(f"room-{roomID}", queue)
