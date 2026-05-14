# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from typing import Protocol, runtime_checkable
from uuid import UUID
import asyncio


@runtime_checkable
class Game(Protocol):
    minPlayers: int = 2
    UUIDs: list[UUID]
    genericState: list
    playerNames: dict[UUID, str]
    points: dict[UUID, int]
    name: str
    description: str
    renewStateEvent: asyncio.Event

    def getState(self) -> dict:
        ...

    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    def turnUUID(self) -> UUID:
        ...

    def addPlayer(self, uuid: UUID, username: str) -> None:
        ...

    async def parseMessage(self, data: dict) -> dict | None:
        ...
