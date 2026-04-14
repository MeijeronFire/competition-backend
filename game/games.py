# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from random import randint
from typing import Optional, Generator, Tuple
from pydantic import BaseModel, ConfigDict, ValidationError
from uuid import UUID
"""
Woop woop game layer
"""

class gameCore:
    def __init__(self):
        self.playerNames: dict[UUID, str] = {}
        self.UUIDs: list[UUID] = []
        self.turnNr = 0
    
    def addPlayer(self, uuid: UUID, username: str):
        self.UUIDs.append(uuid)
        self.playerNames[uuid] = username

    def turn(self):
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.turnNr % len(self.playerNames)

    def turnUUID(self):
        if len(self.playerNames) == 0:
            raise Exception("Error: no players, so cannot get turn.")
        return self.UUIDs[self.turn()]

    # must also be filled by subclass
    def parsePacket(self, packet: str, uuid: UUID):
        raise NotImplementedError

    # hooks to be filled by subclasses
    def _onRegister(self):
        raise NotImplementedError


class moveMessage(BaseModel):
    choice: str
    model_config = ConfigDict(extra="allow")

class fillMessage(BaseModel):
    choice: str = "fillAmount"
    amount: int
    model_config = ConfigDict(extra="allow")

class Uber(gameCore):
    def __init__(self):
        super().__init__()
        self.glasses = [0, 0, 0, 0, 0, 0]
        self.points: dict[UUID, int] = {}
        self.optOutPenalty = 300
        self._parser = self._parseMessage()
        next(self._parser)
    
    def addPlayer(self, uuid: UUID, username: str):
        self.UUIDs.append(uuid)
        self.playerNames[uuid] = username
        self.points[uuid] = 0

    def parseMessage(self, msg: dict) -> dict | None:
        return self._parser.send(msg)

    def _parseMessage(self) -> Generator[dict | None, dict, None]:
        # main game loop
        result = None
        while 1:
            data = yield result
            msg = moveMessage.model_validate(data)
            match msg.choice:
                case "optOut":
                    # add the points due to the opt-outing
                    self.points[self.turnUUID()] += self.optOutPenalty
                    # now it is the next players turn
                    self.turnNr += 1
                case "roll":
                        # throw the dice
                        recentThrow = randint(0, len(self.glasses) - 1)
                        # if that glass is not empty
                        if self.glasses[recentThrow] != 0:
                            # penalize the player, empty the glass
                            # and wait for their next move
                            self.points[self.turnUUID()] += self.glasses[recentThrow]
                            self.glasses[recentThrow] = 0
                            continue
                        
                        # now we can assume that that glass is empty
                        # thus we want to get a "fill" packet
                        data = yield {
                            "type": "fillAmount"
                        }
                        try:
                            msg = fillMessage.model_validate(data)
                        except ValidationError:
                            raise Exception("Error: Did not send correct fill message")
                        
                        # Now fill by that amount and go to next turn
                        self.glasses[recentThrow] += msg.amount
                        print(f"got fillamount: {msg.amount}")
                        self.turnNr += 1

                case _:
                    print(f"Illegal operation: chose {msg.choice}.")
                    result = None
