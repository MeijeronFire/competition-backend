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

import logging
# TODO: replace most print statements by LOG statements throughout this code
logger = logging.getLogger(__name__)


class GameSupervisor():
    def __init__(
        self,
        queue: asyncio.Queue[tuple[UUID, dict]],
        rMgr: RoomManager
    ):
        self._queue = queue
        self._rMgr = rMgr

        self._task: asyncio.Task[dict | None] | None = None
        self.admins: list[UUID] = []

    async def sendToAdmins(self, msg: dict) -> None:
        for admin in self.admins:
            await self._queue.put((
                admin,
                msg
            ))

    async def _create(self, data: dict[str, str]) -> None:
        """
        On a create request, we tell the room manager to create a
        room of a type specified in the request
        """
        try:
            msg = DashCreateMsg.model_validate(data)
        except ValidationError:
            return

        roomID = self._rMgr.create(msg.name)
        if roomID is None:
            return  # do some better error handling here

        await self.sendToAdmins({
            "type": "create",
            "data": self._rMgr.rooms[roomID].toState(),
        })

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
        await self._rMgr.delete(roomID)
        # and inform users of the delete
        await self.sendToAdmins({
            "type": "delete",
            "data": {
                "id": roomID
            }
        })

    async def _getState(self, msg: dict) -> None:
        logger.info(self._rMgr.buildState())
        await self.sendToAdmins({
            "type": "fullState",
            "data": self._rMgr.buildState()
        })

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
