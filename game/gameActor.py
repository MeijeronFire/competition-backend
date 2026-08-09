# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
import logging
from typing import Any, Literal

from app.utils import log_async_error
from game.models import Game
from uuid import UUID
import random

logger = logging.getLogger(__name__)


class GameActor:
    def __init__(
        self,
        game: Game,
        id: int,
        inbox: asyncio.Queue[tuple[UUID, dict[Any, Any]]],
        outbox: asyncio.Queue[tuple[UUID, dict[str, Any]]],
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
        self._ioTask: asyncio.Task[None] | None = None
        self._adminTask: asyncio.Task[None] | None = None
        self._gameTask: asyncio.Task[None] | None = None
        # we want to make sure that the game can not be joined on init,
        # so we enforce an initial closed state
        self.game.roomState = "closed"

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

        self.game.stop()
        logger.info(f"killed game {self.game.name}, id: {self.id}")

    # generate the badges displayed on the dashboard
    def _genBadges(self) -> list[dict[str, str]]:
        # add elements from the gameclass
        badges: list[dict[str, str]] = []

        # (empty)
        if len(self.game.UUIDs) == 0:
            badges.append({"type": "danger", "msg": "empty"})

        if self.game.roomState == "open":
            badges.append({"type": "info", "msg": "open"})
        elif self.game.roomState == "closed":
            badges.append({"type": "warning", "msg": "closed"})
        elif self.game.roomState == "running":
            badges.append({"type": "secondary", "msg": "running"})
        elif self.game.roomState == "stopped":
            badges.append({"type": "warning", "msg": "stopped"})

        return badges

    def toState(self) -> dict[str, Any]:
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

    def setGame(
        self, operation: Literal["start", "stop", "open", "close", "reset"]
    ) -> None:
        # we need to tell both the dashboard and the game that we
        # have changed the state

        # NOTE: if the queue is full, we drop it, so we don't add it.
        # We assume that the next load will include the state. That means
        # that it is the resonsibility of the rest of the code to include its state

        # note: if I would hate myself, I would say:
        # eval(f"self.game.{operation}()")
        match operation:
            case "start":
                self.game.start()
            case "stop":
                self.game.stop()
            case "close":
                self.game.close()
            case "open":
                self.game.open()
            case "reset":
                self.game.reset()
        try:
            self.adminOutbox.put_nowait(
                ("dashboard", {"type": "update", "data": self.toState()})
            )
            # not sure what to put here yet
            # self.adminOutbox.put_nowait((f"room-{self.id}", msg))
        except asyncio.QueueFull:
            pass

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

    async def kickPlayer(self, uuid: UUID) -> None:
        await self.popPlayer(uuid)

    async def adminEvents(self) -> None:
        while True:
            # wait for us to have to resend a packet
            await self.renewStateEvent.wait()
            await self.adminOutbox.put(
                ("dashboard", {"type": "update", "data": self.toState()})
            )
            await self.adminOutbox.put(
                (
                    f"room-{self.id}",
                    {"type": "glassesEvent", "data": self.game.genericState},
                )
            )
            self.renewStateEvent.clear()

    async def runIo(self) -> None:
        oldturn = 0
        while True:
            # TODO: make this depend on other factors!
            if self.game.turnNr != oldturn:
                oldturn = self.game.turnNr
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(0.1)

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
