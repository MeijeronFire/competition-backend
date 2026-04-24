# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from random import randint
from pydantic import BaseModel, ConfigDict, ValidationError
from uuid import UUID
from game.models import Game

class moveMsg(BaseModel):
    choice: int
    row: int
    column: int

class Othello():
    def __init__(self):
        self.UUIDs: list[UUID] = []
        self.genericState: list = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        self.playerNames: dict[UUID, str] = {}
        self.points: dict[UUID, int] = {}
        self.turnNr = 2
        self.minPlayers = 2

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    def turnUUID(self) -> UUID:
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.UUIDs[self.turnNr % 2]

    def addPlayer(self, uuid: UUID, username: str) -> None:
        self.UUIDs.append(uuid)
        self.playerNames[uuid] = username
        self.points[uuid] = 0

    async def parseMessage(self, data: dict) -> dict | None:
        msg = moveMsg.model_validate(data)
        match msg.choice:
            case _:
                pass

_check: Game = Othello()