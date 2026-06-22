# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford
from app.models.primitives import Actor
from app.core import RoomManager
import asyncio
from pydantic import ValidationError
from uuid import UUID
from app.auth.crypt import computeJSONHash

import logging

# TODO: replace most print statements by LOG statements throughout this code
logger = logging.getLogger(__name__)


class GameSupervisor:
    def __init__(self, rMgr: RoomManager):
        self._adminOutbox = rMgr.adminOutbox
        self._rMgr = rMgr

        self._task: asyncio.Task[dict | None] | None = None
        self.admins: list[UUID] = []

    def generateStateHash(self) -> str:
        state = self._rMgr.buildState()
        # logger.info(f"{state} with hash {computeJSONHash(state)}")
        return computeJSONHash(state)

    async def create(self, gameName: str) -> None:
        """
        On a create request, we tell the room manager to create a
        room of a type specified in the request
        """

        roomID = await self._rMgr.create(gameName)
        if roomID is None:
            return  # TODO: do some better error handling here

        await self._adminOutbox.put(
            (
                "dashboard",
                {
                    "type": "create",
                    "data": self._rMgr.rooms[roomID].toState(),
                    "stateHash": self.generateStateHash(),
                },
            )
        )

    async def kick(self, roomID: int, targetUUID: UUID):
        await self._rMgr.rooms[roomID].kickPlayer(targetUUID)

    async def delete(self, roomID: int) -> None:
        """
        On a delete request, we gracefully handle the deletion
        of all objects. We choose the room by the room_id
        """
        await self._rMgr.delete(roomID)
        # and inform users of the delete
        await self._adminOutbox.put(
            (
                "dashboard",
                {
                    "type": "delete",
                    "data": {"id": roomID},
                    "stateHash": self.generateStateHash(),
                },
            )
        )
