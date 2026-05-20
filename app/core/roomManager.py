# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
from uuid import UUID

from game import GameActor
from game import Uber, Othello, Example, TestGame

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
        self.outbox = outbox
        self.adminOutbox = adminOutbox
        # THIS IS BAD
        # THIS IS BAD
        # THIS IS BAD
        self.games = {
            "uber": Uber,
            "othello": Othello,
            "example": Example,
            "testGame": TestGame
        }

    async def create(self, game: str) -> int | None:
        # room_id = randint(10000, 99999)
        if game not in self.games.keys():
            # maybe should be raise ?
            print(
                f"\033[1;33mWARNING: \033[0m Provided game `{game}' does not exist!")
            return

        # so run until there is a proper random number
        # while (roomID := randint(10000, 99999)) in self.rooms.keys():
            # pass
        # TMP, for testing purposes
        roomID = 1
        if self.rooms.keys():
            roomID = sorted(self.rooms.keys())[-1] + 1  # largest + 1

        print(f"\033[1;32mINFO:\t\033[0m  Instantiated {game} at {roomID}")
        inbox: asyncio.Queue[tuple[UUID, dict]] = asyncio.Queue()
        actor = GameActor(
            self.games[game](),
            roomID,
            inbox,
            self.outbox,
            self.adminOutbox
        )
        self.rooms[roomID] = actor
        await actor.start()
        return roomID

    async def delete(self, roomID: int) -> None:
        toBeDel = self.rooms[roomID].game.name
        if roomID not in self.rooms.keys():
            print("useless ID provided.")
            return
        await self.rooms[roomID].stop()
        self.rooms.pop(roomID)
        print(
            f"\033[1;32mINFO:\t\033[0m  Killed {toBeDel} at {roomID}")
        # maybe call some sort of destructor on the object itself?

    # the "official" way to build the complete state
    def buildState(self) -> dict:
        # The format of the general state of the game can be determined
        # here, so that the state in the game implementation is more lean.
        state = {}
        for room in self.rooms.keys():
            state[room] = self.rooms[room].toState()
        return state
