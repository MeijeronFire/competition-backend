import asyncio
from abc import ABC, abstractmethod

class Actor(ABC):
    def __init__(self, queue):
        self.queue = asyncio.Queue()
        self._task: asyncio.Task[dict | None] | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            await self._task
    
    @abstractmethod
    async def _loop(self) -> None:
        while True:
            input = await self.queue.get()
            ... # some handling function
            self.queue.task_done()