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
        self._nr: int = randint(1, 9)
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

    # the fact that this is asynchronous is mostly an interface
    # constraint, but the game may want to work with queues
    # or some other way to maintain state between function calls.
    async def parseMessage(self, data: dict) -> dict | None:
        msg = GuessMsg.model_validate(data)
        if msg.choice != "guess":
            return {
                "type": "error",
                "errorType": f"No valid choice provided. Got {msg.choice}, expected `guess'"
            }
        if msg.guess == self._nr:
            print(self.points)
            print(self.turnUUID())
            self.points[self.turnUUID()] += 1
            # this may trigger twice if the last player in the turn 
            # guesses correctly, but this should not cause any
            # side effects!
            self._newTurn()
        
        # turn is over, go to next player
        self.turnNr += 1

        # if all players have gone we reset the turn counter
        if self.turnNr == 2:
            self.turnNr = 0

_check: Game = Example()