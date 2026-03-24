# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from .game import Game
from random import randint
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
"""
Woop woop game layer
"""


class BaseMessage(BaseModel):
    move: str
    amount: Optional[int] = None
    model_config = ConfigDict(extra="allow")

class RegisterPacket(BaseMessage):
    action: str = "register"
    name: str
    room: str


class Uber(Game):
    def __init__(self):
        super().__init__()
    def parseMessage(self, msg: str, uuid: UUID):
        print(f"Got packet: {msg}")
        