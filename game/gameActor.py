# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
from typing import Any, AsyncIterable

from platformdirs.android import _android_documents_folder
from app.core import roomManager
from app.utils import log_async_error
from game.models import Game
from uuid import UUID
import random


class GameActor:
    def __init__(
        self,
        game: Game,
        id: int,
        inbox: asyncio.Queue[tuple[UUID, dict]],
        outbox: asyncio.Queue[tuple[UUID, dict]],
        adminOutbox: asyncio.Queue[tuple[str, dict[str, Any]]],
    ):
        self.game = game
        self.inbox = inbox
        self.outbox = outbox
        self.adminOutbox = adminOutbox
        self.renewStateEvent = game.renewStateEvent
        self.id = id
        self.borderType = getattr(
            self.game,
            "borderType",
            random.choice(
                [
                    "primary",
                    "secondary",
                    "success",
                    "danger",
                    "warning",
                    "info",
                    "light",
                    "dark",
                ]
            ),
        )
        self._ioTask: asyncio.Task[None | None] | None = None
        self._adminTask: asyncio.Task[None | None] | None = None
        # we want to make sure that the game can not be joined on init,
        # so we enforce an initial closed state
        self.game.closed = True

    async def start(self) -> None:
        # init general message io
        self._ioTask = asyncio.create_task(self.runIo())
        self._ioTask.add_done_callback(log_async_error)
        # init other IO
        self._adminTask = asyncio.create_task(self.adminEvents())
        self._adminTask.add_done_callback(log_async_error)

    async def stop(self) -> None:
        if self._ioTask:
            self._ioTask.cancel()
            try:
                await self._ioTask
            except asyncio.CancelledError:
                pass

        if self._adminTask:
            self._adminTask.cancel()
            try:
                await self._adminTask
            except asyncio.CancelledError:
                pass

    # generate the badges displayed on the dashboard
    def _genBadges(self):
        # add arbitrary elements from the gameclass
        badges = [] + getattr(self.game, "roomState", [])

        # (empty)
        if len(self.game.UUIDs) == 0:
            badges.append({"type": "danger", "msg": "empty"})

        # (closed)
        if self.game.closed:
            badges.append({"type": "warning", "msg": "closed"})
        # (open)
        else:
            badges.append({"type": "primary", "msg": "open"})
        return badges

    def toState(self):
        return {
            "playerNr": len(self.game.UUIDs),
            "minPlayers": self.game.minPlayers,
            "title": self.game.name,
            "id": self.id,
            "gameState": self.game.getState(),
            "description": self.game.description,
            "borderType": self.borderType,
            "roomState": self._genBadges(),
        }

    async def addPlayer(self, uuid: UUID, username: str) -> None:
        await self.adminOutbox.put(
            (
                f"room-{self.id}",
                {"type": "newPlayer", "data": {"UUID": str(uuid), "name": username}},
            )
        )
        self.game.addPlayer(uuid, username)

    async def popPlayer(self, uuid: UUID) -> None:
        await self.adminOutbox.put(
            (f"room-{self.id}", {"type": "delPlayer", "data": {"UUID": str(uuid)}})
        )
        self.game.popPlayer(uuid)

    async def adminEvents(self):
        while True:
            # wait for us to have to resend a packet
            await self.renewStateEvent.wait()
            await self.adminOutbox.put(
                ("dashboard", {"type": "update", "data": self.toState()})
            )
            self.renewStateEvent.clear()

    async def runIo(self):
        await self.game.start()
        while True:
            # TODO: make this depend on other factors!
            await asyncio.sleep(1)
            # print(self.game.points)
            # print(self.game.playerNames)
            if len(self.game.UUIDs) < self.game.minPlayers:
                # print(f"{self.game.__str__()}: skipped. {len(self.game.UUIDs)} / 2")
                continue

            # the client object who's turn it is
            sentTo = self.game.turnUUID()
            # tell client it is his turn
            await self.outbox.put(
                (sentTo, {"type": "turn", "state": self.game.genericState})
            )
            while True:
                while True:
                    # until we get the message we want
                    sender, msg = await self.inbox.get()
                    # print(f"{sentTo}: Got {sender}, {msg}")
                    if sender == sentTo:
                        break

                resp = await self.game.parseMessage(msg)

                if resp is None:
                    break

                # thus it is a dict, game.parseMessage(dict) -> dict | None
                await self.outbox.put((sender, resp))
