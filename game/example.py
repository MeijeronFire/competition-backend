# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

"""
This example shows how a game could be implemented.

It has two players, generates a random number between
1 and 10 (exclusive), and awards a point to the player that
has correctly guessed the number. If all players have
guessed, a new number is chosen.
"""

from random import randint
from pydantic import BaseModel, ValidationError
from uuid import UUID
from game.models import Game

# any incoming message needs to look like this. For example:
# {
#   "choice": "guess",
#   "guess": 4
# }
class GuessMsg(BaseModel):
    choice: str
    guess: int

class Example():
    def __init__(self):
        self.UUIDs: list[UUID] = []
        self.genericState: list = []
        self.playerNames: dict[UUID, str] = {}
        self.points: dict[UUID, int] = {}
        self.turnNr = 0
        self._nr: int
        self.minPlayers = 2

    async def start(self) -> None:
        pass
    async def stop(self) -> None:
        pass

    def turnUUID(self) -> UUID:
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.UUIDs[self.turnNr % len(self.UUIDs)]

    def addPlayer(self, uuid: UUID, username: str) -> None:
        self.UUIDs.append(uuid)
        self.playerNames[uuid] = username
        self.points[uuid] = 0
    
    def _newTurn(self) -> None:
        self._nr = randint(1, 9)

    async def parseMessage(self, data: dict) -> dict | None:
        msg = GuessMsg.model_validate(data)
        if msg.choice != "guess":
            return {
                "type": "error",
                "errorType": f"No valid choice provided. Got {msg.choice}, expected `guess'"
            }
        if msg.guess == self._nr:
            self.points[self.turnUUID()] += 1
        
        # turn is over, go to next player
        self.turnNr += 1

        # if every player has gone:
        if self.turnNr == len(self.UUIDs):
            self._newTurn()
            self.turnNr = 1

_check: Game = Example()