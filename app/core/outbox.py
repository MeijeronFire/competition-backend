# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from app.models.primitives import Actor
from app.core import ConnectionMgr
import asyncio


# example of our actor definition
class Sender(Actor):
    def __init__(self, queue: asyncio.Queue, cMgr: ConnectionMgr):
        self.queue = queue
        self.cMgr = cMgr

    async def _loop(self):
        while True:
            # wait for something to send
            target_id, msg = await self.queue.get()
            # find the connection of the target to send it to
            target = self.cMgr.clients[target_id]
            # send it
            await target.ws.send_json(msg)
            # mark task as complete
            self.queue.task_done()
            # and repeat               ^
            #                          |
            # -------------------------+
