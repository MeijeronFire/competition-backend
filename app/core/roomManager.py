# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
from uuid import UUID

from game import GameActor
from game import Uber, Othello, Example

from random import randint

import traceback


def log_async_error(task: asyncio.Task):
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        traceback.print_exc()


class RoomManager():
    def __init__(self, outbox: asyncio.Queue[tuple[UUID | str, dict]]):
        self.rooms: dict[int, GameActor] = {}
        self.tasks: dict[int, asyncio.Task] = {}
        self.allRooms: list[int] = []
        self.outbox = outbox
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
        while (room_id := randint(10000, 99999)) in self.allRooms:
            pass

        print(f"\033[1;32mINFO:\t\033[0m  Instantiated {game} at {room_id}")
        inbox: asyncio.Queue[tuple[UUID, dict]] = asyncio.Queue()
        actor = GameActor(self.games[game](), inbox, self.outbox)
        self.rooms[room_id] = actor
        self.allRooms.append(room_id)
        self.tasks[room_id] = asyncio.create_task(actor.run())
        self.tasks[room_id].add_done_callback(log_async_error)
        return room_id

    async def delete(self, roomID: int) -> None:
        if roomID not in self.rooms.keys():
            print("useless ID provided.")
            return
        gameName = self.rooms[roomID].game.name
        self.tasks[roomID].cancel()
        try:
            await self.tasks[roomID]
        except asyncio.CancelledError:
            pass
        self.tasks.pop(roomID)
        self.rooms.pop(roomID)
        self.allRooms.remove(roomID)
        print(f"\033[1;32mINFO:\t\033[0m  Killed {gameName} at {roomID}")
        # maybe call some sort of destructor on the object itself?
