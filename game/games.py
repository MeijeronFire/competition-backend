# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from random import randint
from pydantic import BaseModel, ConfigDict, ValidationError
from uuid import UUID
from game.models import Game
import asyncio
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

class Uber():
    def __init__(self) -> None:
        self.glasses = [0, 0, 0, 0, 0, 0]
        self.genericState = self.glasses
        self.points: dict[UUID, int] = {}
        self.optOutPenalty = 200
        self.playerNames: dict[UUID, str] = {}
        self.UUIDs: list[UUID] = []
        self.turnNr = 0

        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._sendQueue: asyncio.Queue[dict | None] = asyncio.Queue()
        self._recvQueue: asyncio.Queue[dict] = asyncio.Queue()
    
    def addPlayer(self, uuid: UUID, username: str):
        self.UUIDs.append(uuid)
        self.playerNames[uuid] = username
        self.points[uuid] = 0

    def turn(self):
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.turnNr % len(self.playerNames)

    def turnUUID(self) -> UUID:
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.UUIDs[self.turn()]

    async def start(self) -> None:
        self._task = asyncio.create_task(self._gameLoop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)

    async def parseMessage(self, msg: dict) -> dict | None:
        await self._recvQueue.put(msg)
        return await self._sendQueue.get()

    async def _gameLoop(self) -> None:
        # main game loop
        while 1:
            data = await self._recvQueue.get()
            msg = moveMessage.model_validate(data)
            match msg.choice:
                case "optOut":
                    # add the points due to the opt-outing
                    self.points[self.turnUUID()] += self.optOutPenalty
                    # now it is the next players turn
                    self.turnNr += 1
                    print("turn ended")
                    result = None
                case "roll":
                        # throw the dice
                        recentThrow = randint(0, len(self.glasses) - 1)
                        # if that glass is not empty
                        if self.glasses[recentThrow] != 0:
                            # penalize the player, empty the glass
                            # and wait for their next move
                            self.points[self.turnUUID()] += self.glasses[recentThrow]
                            self.glasses[recentThrow] = 0
                            result = None
                            await self._sendQueue.put(None)
                            continue
                        
                        # now we can assume that that glass is empty
                        # thus we want to get a "fill" packet
                        # data = yield {
                        #     "type": "fillAmount"
                        # }
                        await self._sendQueue.put({
                            "type": "fillAmount"
                        })
                        data = await self._recvQueue.get()
                        try:
                            msg = fillMessage.model_validate(data)
                        except ValidationError:
                            raise Exception("Error: Did not send correct fill message")
                        
                        # Now fill by that amount and go to next turn
                        self.glasses[recentThrow] += msg.amount
                        self.turnNr += 1
                        print("turn ended")
                        result = None
                case "getState":
                    await self._sendQueue.put({"type": "state", "state": self.glasses})
                case _:
                    print(f"Illegal operation: chose {msg.choice}.")
                    result = None
            # every path must have some sort of response to put
            await self._sendQueue.put(None)

# compile time verification
_check: Game = Uber()

class Othello():
    def __init__(self):
        UUIDs: list[UUID] = []
        genericState: list = []
        playerNames: dict[UUID, str] = {}
        points: dict[UUID, int] = {}

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