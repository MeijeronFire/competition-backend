# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from typing import Protocol, runtime_checkable
from uuid import UUID

@runtime_checkable
class Game(Protocol):
    UUIDs: list[UUID]
    genericState: list
    playerNames: dict[UUID, str]
    points: dict[UUID, int]

    async def start(self) -> None:
        ...
    async def stop(self) -> None:
        ...
    def turnUUID(self) -> UUID:
        ...
    def addPlayer(self, uuid: UUID, username: str) -> None:
        ...
    async def parseMessage(self, msg: dict) -> dict | None:
        ...