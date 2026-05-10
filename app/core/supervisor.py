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
from uuid import UUID


class GameSupervisor():
    def __init__(self, queue: asyncio.Queue[tuple[UUID | str, dict]], rMgr: RoomManager):
        self.queue = queue
        self.rMgr = rMgr
        self._task: asyncio.Task[dict | None] | None = None

    async def _create(self, data: dict[str, str]) -> None:
        """
        On a create request, we tell the room manager to create a
        room of a type specified in the request
        """
        try:
            msg = DashCreateMsg.model_validate(data)
        except ValidationError:
            return

        roomID = self.rMgr.create(msg.name)
        if roomID is None:
            return  # do some better error handling here

        await self.queue.put(("admin", {
            "type": "create",
            "data": {
                "playerNr": 0,
                "minPlayers": 2,
                "title": self.rMgr.rooms[roomID].game.name,
                "id": roomID
            }}))

    def _update(self, data: dict) -> None:
        """
        On an update request, we look at the type of update.
        Currently we support closing a room and starting a room.
        """
        try:
            msg = DashUpdateMsg.model_validate(data)
        except ValidationError:
            return

    async def _delete(self, data: dict[str, int]) -> None:
        """
        On a delete request, we gracefully handle the deletion
        of all objects. We choose the room by the room_id
        """
        try:
            msg = DashDeleteMsg.model_validate(data)
        except ValidationError:
            return
        roomID = msg.roomID
        await self.rMgr.delete(roomID)

    async def _getState(self, msg: dict) -> None:
        print(self.rMgr.buildState())
        await self.queue.put(("admin", {
            "type": "fullState",
            "data": self.rMgr.buildState()}))

    async def parse(self, action: str, msg: dict):
        # implementation of our simple CRUD interface
        match action:
            case "create":
                await self._create(msg)
            case "update":
                self._update(msg)
            case "delete":
                await self._delete(msg)
            case "getState":
                await self._getState(msg)
            case _:
                raise Exception("Improper command provided to supervisor")
