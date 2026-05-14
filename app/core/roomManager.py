# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
from uuid import UUID

from game import GameActor
from game import Uber, Othello, Example

from app.auth.crypt import computeJSONHash
from app.utils import log_async_error

from random import randint


class RoomManager():
    def __init__(
        self,
        outbox: asyncio.Queue[tuple[UUID, dict]],
        adminOutbox: asyncio.Queue[dict]
    ):
        self.rooms: dict[int, GameActor] = {}
        self._tasks: dict[int, asyncio.Task] = {}
        self.outbox = outbox
        self.adminOutbox = adminOutbox
        # THIS IS BAD
        # THIS IS BAD
        # THIS IS BAD
        self.games = {
            "uber": Uber,
            "othello": Othello,
            "example": Example
        }

    def create(self, game: str) -> int | None:
        # room_id = randint(10000, 99999)
        if game not in self.games.keys():
            # maybe should be raise ?
            print(
                f"\033[1;33mWARNING: \033[0m Provided game `{game}' does not exist!")
            return

        # so run until there is a proper random number
        while (roomID := randint(10000, 99999)) in self.rooms.keys():
            pass

        print(f"\033[1;32mINFO:\t\033[0m  Instantiated {game} at {roomID}")
        inbox: asyncio.Queue[tuple[UUID, dict]] = asyncio.Queue()
        actor = GameActor(
            self.games[game](),
            roomID,
            inbox,
            self.outbox
        )
        self.rooms[roomID] = actor
        self._tasks[roomID] = asyncio.create_task(actor.run())
        self._tasks[roomID].add_done_callback(log_async_error)
        return roomID

    async def delete(self, roomID: int) -> None:
        if roomID not in self.rooms.keys():
            print("useless ID provided.")
            return
        gameName = self.rooms[roomID].game.name
        self._tasks[roomID].cancel()
        try:
            await self._tasks[roomID]
        except asyncio.CancelledError:
            pass
        self._tasks.pop(roomID)
        self.rooms.pop(roomID)
        print(f"\033[1;32mINFO:\t\033[0m  Killed {gameName} at {roomID}")
        # maybe call some sort of destructor on the object itself?

    # the "official" way to build the complete state
    def buildState(self) -> dict:
        # The format of the general state of the game can be determined
        # here, so that the state in the game implementation is more lean.
        state = {}
        for room in self.rooms.keys():
            state[room] = self.rooms[room].toState()
        return state
