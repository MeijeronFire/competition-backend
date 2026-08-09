# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import logging
import random
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from game.models import Game
import asyncio

logger = logging.getLogger(__name__)

"""
Woop woop game layer
"""


class moveMessage(BaseModel):
    choice: str
    model_config = ConfigDict(extra="allow")


class fillMessage(BaseModel):
    choice: str = "fillAmount"
    amount: int
    model_config = ConfigDict(extra="allow")


class TestGame:
    def __init__(self) -> None:
        self.name = "TestGame"
        self.description = f"""
            <span class="text-danger">Demonstration of HTML injection</span>
            And some other business
        """
        self.minPlayers = 2

        self.glasses = [0, 0, 0, 0, 0, 0]
        self.genericState = self.glasses
        self.points: dict[UUID, int] = {}
        self.optOutPenalty = 200
        self.playerNames: dict[UUID, str] = {}
        self.UUIDs: list[UUID] = []
        self.turnNr = 0
        self.roomState: Literal["open", "closed", "running", "stopped"] = "closed"

        self._running = False
        self._task = asyncio.create_task(self._gameLoop())
        self._sendQueue: asyncio.Queue[dict[Any, Any] | None] = asyncio.Queue()
        self._recvQueue: asyncio.Queue[dict[Any, Any]] = asyncio.Queue()
        # bit of an ugly hack, but it will work
        self.renewStateEvent = asyncio.Event()

    def getState(self) -> dict[Any, Any]:
        return {}

    def addPlayer(self, uuid: UUID, username: str):
        self.UUIDs.append(uuid)
        self.playerNames[uuid] = username
        self.points[uuid] = 0

    def popPlayer(self, uuid: UUID) -> None:
        self.UUIDs.remove(uuid)
        self.playerNames.pop(uuid)
        self.points.pop(uuid)

    def turn(self):
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.turnNr % len(self.playerNames)

    def turnUUID(self) -> UUID:
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.UUIDs[self.turn()]

    def start(self) -> None:
        self.roomState = "running"

    def stop(self) -> None:
        self.roomState = "stopped"
        if self._task:
            self._task.cancel()

    def open(self) -> None:
        self.roomState = "open"

    def close(self) -> None:
        self.roomState = "closed"

    def reset(self) -> None:
        self.roomState = "closed"

    async def parseMessage(self, data: dict[str, Any]) -> dict[str, Any] | None:
        await self._recvQueue.put(data)
        return await self._sendQueue.get()

    async def _gameLoop(self) -> None:
        # main game loop
        try:
            while True:
                # print('waiting')
                await asyncio.sleep(5)
                # we need some way to update the so-called "room-state"
                # since the message digest is calculated seperately, we
                # simply update the state and afterwars push to clients

                # self.roomState = [
                #     {
                #         "type": random.choice(
                #             [
                #                 "primary",
                #                 "secondary",
                #                 "success",
                #                 "danger",
                #                 "warning",
                #                 "info",
                #                 "light",
                #                 "dark",
                #             ]
                #         ),
                #         "msg": "Pr.OfConc.",
                #     }
                # ]
                self.description = (
                    'The quick brown fox <span class="text-warning">'
                    + random.choice(["jumps", "sits", "sleeps", "cries", "laughs"])
                    + "</span> over the lazy dog."
                )
                self.renewStateEvent.set()
        except asyncio.CancelledError:
            pass


# compile time verification
_check: Game = TestGame()
