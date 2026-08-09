# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
from abc import ABC, abstractmethod
from app.utils import log_async_error


class Actor(ABC):
    """Actor class

    This class models what an actor looks like in this codebase. It is an asynchronous
    worker that has some internal state, reads / writes items to / from a queue, can
    be started and stopped, and logs errors when they occur.

    Args:
        Abstract Class (abc.ABC): Inheritance to mark this class as abstract
    """

    def __init__(self, queue):
        self.queue = asyncio.Queue()
        self._task: asyncio.Task[dict | None] | None = None

    async def start(self) -> None:
        """start
        Creates a task for self._read() and adds a callback to log errors
        """
        self._task = asyncio.create_task(self._read())
        self._task.add_done_callback(log_async_error)

    async def stop(self) -> None:
        """stop
        Cancels self._task and safely waits for it to stop
        """
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    @abstractmethod
    async def _read(self) -> None:
        """_read
        General worker function. Is purely abstract and should be overwritten.
        Implementation below serves only as an example.
        """
        while True:
            input = await self.queue.get()
            ...  # some handling function
            self.queue.task_done()
