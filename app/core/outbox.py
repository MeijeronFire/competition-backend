# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import logging
from typing import Any

from griffe import DocstringSectionAttributes

from app.models.primitives import Actor
from app.core.connections import ConnectionMgr, Client
from app.core.supervisor import GameSupervisor
import asyncio
from uuid import UUID

logger = logging.getLogger(__name__)


# example of our actor definition
class AdminStream(Actor):
    def __init__(
        self,
        adminQueue: asyncio.Queue[tuple[str, dict[str, Any]]],
        supervisor: GameSupervisor,
    ):
        self.queueIn = adminQueue
        self._outQueues: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}
        self._supervisor = supervisor

    def addAdmin(
        self, destination: str, queue: asyncio.Queue[dict[str, Any]]
    ) -> None:
        if destination not in self._outQueues:
            self._outQueues[destination] = []
        self._outQueues[destination].append(queue)

    def popAdmin(
        self, destination: str, queue: asyncio.Queue[dict[str, Any]]
    ) -> None:
        self._outQueues[destination].remove(queue)

    async def _read(self):
        while True:
            # wait for something to send
            msg = await self.queueIn.get()

            # first argument is destination
            destination = msg[0]
            if destination not in self._outQueues:
                logger.info("Destination not yet known")
                continue
            outGoingQueues = self._outQueues[destination]

            # second argument is content
            data = msg[1]

            # send it to all relevant clients
            await asyncio.gather(*(q.put(data) for q in outGoingQueues))

            # mark as done, repeat
            self.queueIn.task_done()


class Sender(Actor):
    def __init__(self, queue: asyncio.Queue[tuple[UUID, dict]], cMgr: ConnectionMgr):
        self.queue = queue
        self.cMgr = cMgr

    async def _read(self):
        while True:
            # wait for something to send
            targetID, msg = await self.queue.get()
            # find the connection of the target to send it to
            target = self.cMgr.clients[targetID]
            # send it
            await target.ws.send_json(msg)
            # mark task as complete
            self.queue.task_done()
            # and repeat               ^
            #                          |
            # -------------------------+
