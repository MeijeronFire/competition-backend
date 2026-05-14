# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from contextlib import asynccontextmanager
import asyncio
import traceback
from fastapi import FastAPI
from typing import cast
from uuid import UUID

from app.core import ConnectionMgr
from app.core import RoomManager
from app.core import Sender
from app.core import AdminSender
from app.core import GameSupervisor
from app.models.datastructs import StateModel
from app.utils import log_async_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    state = cast(StateModel, app.state)
    # set the maxsize to 100, s.t. if the handling is less than traffic,
    # we block allowing new msgs
    # inbox: asyncio.Queue[Tuple[Client, Dict]] = asyncio.Queue(maxsize = 100)
    outbox: asyncio.Queue[tuple[UUID, dict]] = asyncio.Queue(maxsize=100)
    adminOutbox: asyncio.Queue[dict] = asyncio.Queue(maxsize=100)

    app.state.outbox = outbox
    app.state.outbox = adminOutbox

    rMgr = RoomManager(outbox, adminOutbox)
    app.state.rMgr = rMgr

    cMgr = ConnectionMgr()
    app.state.cMgr = cMgr

    supervisor = GameSupervisor(rMgr)
    app.state.supervisor = supervisor

    # now we instantiate the sender postoffice!
    sender = Sender(outbox, cMgr)
    app.state.sender = sender  # TODO: see where this is used, might be redundant
    await sender.start()

    # Also instantiate the admin sender postoffice!
    adminSender = AdminSender(adminOutbox, cMgr)
    app.state.adminSender = adminSender
    await adminSender.start()

    yield

    await sender.stop()
    await adminSender.start()
    # we don't really care about stopping all games, since no states persist

    # if gameSupervisorTask:
    # gameSupervisorTask.cancel()
