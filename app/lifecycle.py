# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from contextlib import asynccontextmanager
import asyncio
import traceback
from fastapi import FastAPI
from typing import Any, cast
from uuid import UUID
import signal

from app.core import ConnectionMgr
from app.core import RoomManager
from app.core import Sender
from app.core import AdminStream
from app.core import GameSupervisor
from app.models.datastructs import StateModel
from app.utils import log_async_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan

    This is the lifecycle manager of the app. This is broadly used for initializing procceses
    that are dependent on the existence of an app, i.e. extending the functionality and state.

    Specifically here, we initialize the outbox, the room manager, the connection manager,
    the supervisor, the sender and the admin sender.

    If you wish to start up with some pre existing state, this would also be the place to do so.
    When testing, it is common to start with something like:
    ```
    await supervisor._create({"name":"testGame"})
    ```
    Make sure to end all tasks started here as well.

    Args:
        app (FastAPI): The app to which the lifecycle pertains
    """
    state = cast(StateModel, app.state)
    # set the maxsize to 100, s.t. if the handling is less than traffic,
    # we block allowing new msgs
    # inbox: asyncio.Queue[Tuple[Client, Dict]] = asyncio.Queue(maxsize = 100)
    outbox: asyncio.Queue[tuple[UUID, dict]] = asyncio.Queue(maxsize=100)
    adminOutbox: asyncio.Queue[tuple[str, dict[str, Any]]] = asyncio.Queue(
        maxsize=100
    )

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
    adminStream = AdminStream(adminOutbox, supervisor)
    app.state.adminStream = adminStream
    await adminStream.start()

    await supervisor._create({"name": "testGame"})

    app.state.users = 0

    yield

    await sender.stop()
    await adminSender.start()
    # we don't really care about stopping all games, since no states persist

    # if gameSupervisorTask:
    # gameSupervisorTask.cancel()
