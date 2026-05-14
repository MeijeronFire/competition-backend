# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from app.models.primitives import Actor
from app.core.connections import ConnectionMgr, Client
from app.core.supervisor import GameSupervisor
import asyncio
from uuid import UUID


# example of our actor definition
class AdminSender(Actor):
    def __init__(self, adminQueue: asyncio.Queue[dict], cMgr: ConnectionMgr, supervisor: GameSupervisor):
        self.queue = adminQueue
        self._cMgr = cMgr
        self._admins = []
        self._supervisor = supervisor

    def addAdmin(self, client: Client):
        self._admins.append(client)

    def popAdmin(self, client: Client):
        self._admins.remove(client)

    async def _read(self):
        while True:
            # wait for something to send
            msg = await self.queue.get()
            # send it & wrap it in a proper hash
            for admin in self._admins:
                await admin.ws.send_json({**msg, "stateHash": self._supervisor.generateStateHash()})

            # mark as done, repeat
            self.queue.task_done()


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
