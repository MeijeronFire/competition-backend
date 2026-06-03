# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from typing import Protocol, runtime_checkable, Literal
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
    roomState: Literal["open", "closed", "running", "stopped"]

    """Game order

    Broadly the game happens in this order:
        1. __init__(), the game starts playing
        2. open(), players can start joining the game
        3. close(), players can no longer join the game
        4. start(), the game starts
        5. parsemessage() [looped], the game happens
        6. stop(), the game is over but its data still exists and may be examined
        7. parent kills the game
    """

    def getState(self) -> dict: ...

    # when the game starts, so when players can make moves
    def start(self) -> None: ...

    # when the game stops so moves are disallowed
    def stop(self) -> None: ...

    # when we want the game to open, so players can join
    def open(self) -> None: ...

    # when the game closes, we players can not join but the game isn't started yet
    def close(self) -> None: ...

    def turnUUID(self) -> UUID: ...

    def addPlayer(self, uuid: UUID, username: str) -> None: ...

    def popPlayer(self, uuid: UUID): ...

    # TODO: un-async this
    async def parseMessage(self, data: dict) -> dict | None: ...
