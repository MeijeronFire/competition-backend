# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford


from typing import Any
from uuid import UUID

class Game:
    def __init__(self):
        self.playerNames: dict[UUID, str] = {}
        self.UUIDs: list[UUID] = []
        self.turnNr = 0

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