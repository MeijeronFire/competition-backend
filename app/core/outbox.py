# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from app.models.primitives import Actor
from app.core import ConnectionMgr
import asyncio
from uuid import UUID

# example of our actor definition


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
