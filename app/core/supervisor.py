# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford
from app.models.primitives import Actor
from app.models.verify import (
    DashCreateMsg,
    DashDeleteMsg,
    DashUpdateMsg
)
from app.core import RoomManager
import asyncio
from pydantic import ValidationError


class GameSupervisor(Actor):
    def __init__(self, queue: asyncio.Queue[tuple[str, dict]], rMgr: RoomManager):
        self.queue = queue
        self.rMgr = rMgr
        self._task: asyncio.Task[dict | None] | None = None

    def _create(self, msg: dict[str, str]) -> None:
        """
        On a create request, we tell the room manager to create a
        room of a type specified in the request
        """
        try:
            DashCreateMsg.model_validate(msg)
        except ValidationError:
            return
        self.rMgr.create(msg["name"])

    def _update(self, msg: dict) -> None:
        """
        On an update request, we look at the type of update.
        Currently we support closing a room and starting a room.
        """
        try:
            DashUpdateMsg.model_validate(msg)
        except ValidationError:
            return

    def _delete(self, msg: dict[str, int]) -> None:
        """
        On a delete request, we gracefully handle the deletion 
        of all objects. We choose the room by the room_id
        """
        try:
            DashDeleteMsg.model_validate(msg)
        except ValidationError:
            return
        room_id = msg["room_id"]
        self.rMgr.delete(room_id)

    async def _loop(self):
        while True:
            # wait for something to send
            action, msg = await self.queue.get()
            # implementation of our simple CRUD interface
            match action:
                case "create":
                    self._create(msg)
                case "update":
                    self._update(msg)
                case "delete":
                    self._delete(msg)
                case _:
                    raise Exception("Improper command provided to supervisor")
            self.queue.task_done()
            # and repeat               ^
            #                          |
            # -------------------------+
