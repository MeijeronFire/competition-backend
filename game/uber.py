# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from typing import Any, Literal
from uuid import UUID
import asyncio
from pydantic import BaseModel, ConfigDict, ValidationError
from random import randint
from game.models import Game


class moveMessage(BaseModel):
    choice: str
    model_config = ConfigDict(extra="allow")


class fillMessage(BaseModel):
    choice: str = "fillAmount"
    amount: int
    model_config = ConfigDict(extra="allow")


class Uber:
    def __init__(self):
        self.minPlayers: int = 1
        self.UUIDs: list[UUID] = []
        self._glasses = [0, 0, 0, 0, 0, 0]
        self.genericState: list[Any] = self._glasses
        self.playerNames: dict[UUID, str] = {}
        self.points: dict[UUID, int] = {}
        self.name: str = "uber"
        self.description: str = "tmp"
        self.renewStateEvent: asyncio.Event = asyncio.Event()
        self.roomState: Literal["open", "closed", "running", "stopped"]
        self.optOutPenalty = 300

        self.turnNr = 0

        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._sendQueue: asyncio.Queue[dict[Any, Any] | None] = asyncio.Queue()
        self._recvQueue: asyncio.Queue[dict[Any, Any]] = asyncio.Queue()

        self._task = asyncio.create_task(self._gameLoop())

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

    def getState(self) -> dict[str, Any]:
        return {"glasses": self._glasses}

    # when the game starts, so when players can make moves
    def start(self) -> None:
        self.roomState = "running"

    # when the game stops so moves are disallowed
    def stop(self) -> None:
        self.roomState = "stopped"

    # when we want the game to open, so players can join
    def open(self) -> None:
        self.roomState = "open"

    # when the game closes, we players can not join but the game isn't started yet
    def close(self) -> None:
        self.roomState = "closed"

    def reset(self) -> None:
        self.roomState = "closed"

    def turnUUID(self) -> UUID:
        return self.UUIDs[self.turnNr % len(self.UUIDs)]

    def addPlayer(self, uuid: UUID, username: str) -> None:
        self.UUIDs.append(uuid)
        self.playerNames[uuid] = username
        self.points[uuid] = 0

    def popPlayer(self, uuid: UUID):
        self.UUIDs.remove(uuid)
        self.playerNames.pop(uuid)
        self.points.pop(uuid)

    # TODO: un-async this

    async def parseMessage(self, data: dict[str, Any]) -> dict[str, Any] | None:
        await self._recvQueue.put(data)
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
                    self.renewStateEvent.set()
                    print("turn ended")
                case "roll":
                    # throw the dice
                    recentThrow = randint(0, len(self._glasses) - 1)
                    # if that glass is not empty
                    if self._glasses[recentThrow] != 0:
                        # penalize the player, empty the glass
                        # and wait for their next move
                        self.points[self.turnUUID()] += self._glasses[recentThrow]
                        self._glasses[recentThrow] = 0
                        self.renewStateEvent.set()
                        await self._sendQueue.put(None)
                        continue

                    # now we can assume that that glass is empty
                    # thus we want to get a "fill" packet
                    # data = yield {
                    #     "type": "fillAmount"
                    # }
                    await self._sendQueue.put({"type": "fillAmount"})
                    self.renewStateEvent.set()
                    data = await self._recvQueue.get()
                    try:
                        msg = fillMessage.model_validate(data)
                    except ValidationError:
                        raise Exception("Error: Did not send correct fill message")

                    # Now fill by that amount and go to next turn
                    self._glasses[recentThrow] += msg.amount
                    self.turnNr += 1
                    self.renewStateEvent.set()
                    print("turn ended")
                case "getState":
                    await self._sendQueue.put(
                        {"type": "state", "state": self._glasses}
                    )
                case _:
                    print(f"Illegal operation: chose {msg.choice}.")
            # every path must have some sort of response to put
            await self._sendQueue.put(None)


# compile time verification
_check: Game = Uber()
