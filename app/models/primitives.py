# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
import traceback
from abc import ABC, abstractmethod
from app.core import (
    RoomManager,
    ConnectionMgr,
    GameSupervisor,
    Sender
)


class StateModel:
    rMgr: RoomManager
    cMgr: ConnectionMgr
    supervisor: GameSupervisor
    sender: Sender


def log_async_error(task: asyncio.Task):
    try:
        task.result()
    except:
        traceback.print_exc()


class Actor(ABC):
    def __init__(self, queue):
        self.queue = asyncio.Queue()
        self._task: asyncio.Task[dict | None] | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._read())
        self._task.add_done_callback(log_async_error)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            await self._task

    @abstractmethod
    async def _read(self) -> None:
        while True:
            input = await self.queue.get()
            ...  # some handling function
            self.queue.task_done()
