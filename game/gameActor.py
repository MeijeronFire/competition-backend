# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import asyncio
from app.core import roomManager
from game.models import Game
from uuid import UUID

class GameActor():
    def __init__(
            self,
            game: Game,
            inbox: asyncio.Queue[tuple[UUID, dict]],
            outbox: asyncio.Queue[tuple[UUID, dict]]
        ):
        self.game = game
        self.inbox = inbox
        self.outbox = outbox

    async def run(self):
        await self.game.start()
        while True:
            # TODO: make this depend on other factors!
            await asyncio.sleep(1)
            print(self.game.points)
            print(self.game.playerNames)
            if len(self.game.UUIDs) < self.game.minPlayers:
                print(f"{self.game.__str__()}: skipped. {len(self.game.UUIDs)} / 2")
                continue
            
            # the client object whos turn it is
            sentTo = self.game.turnUUID()
            # tell client it is his turn
            await self.outbox.put((
                sentTo, {
                    "type": "turn",
                    "state": self.game.genericState
                }
            ))
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
