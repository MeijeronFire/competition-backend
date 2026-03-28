# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from .game import Game
from random import randint
from typing import Optional, Generator
from pydantic import BaseModel, ConfigDict, ValidationError
from uuid import UUID
"""
Woop woop game layer
"""


class moveMessage(BaseModel):
    choice: str
    model_config = ConfigDict(extra="allow")

class fillMessage(BaseModel):
    choice = "fillAmount"
    amount: int
    model_config = ConfigDict(extra="allow")

class Uber(Game):
    def __init__(self):
        super().__init__()
        self.glasses = [0, 0, 0, 0, 0, 0]
        self.points: dict[UUID, int] = {}
        self.optOutPenalty = 300
    
    def throwDice(self):
        pass

    def parseMessage(self) -> Generator[dict | None, dict, None]:
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
                        recentThrow = randint(1, len(self.glasses))
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
                        self.turnNr += 1

                case _:
                    pass
