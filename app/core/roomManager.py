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
    except:
        traceback.print_exc()


class RoomManager():
    def __init__(self, outbox: asyncio.Queue[tuple[UUID, dict]]):
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

    def create(self, game: str) -> int:
        # room_id = randint(10000, 99999)
        room_id = 10851
        print(f"instantiated {game} at {room_id}")
        inbox: asyncio.Queue[tuple[UUID, dict]] = asyncio.Queue()
        actor = GameActor(self.games[game](), inbox, self.outbox)
        self.rooms[room_id] = actor
        self.allRooms.append(room_id)
        self.tasks[room_id] = asyncio.create_task(actor.run())
        self.tasks[room_id].add_done_callback(log_async_error)
        return room_id

    def delete(self, room_id: int) -> None:
        self.tasks[room_id].cancel()
        self.tasks.pop(room_id)
        # maybe call some sort of destructor on the object itself?
