# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford


from typing import Any
from uuid import UUID

class Game:
    # This should be expanded on by various subclasses,
    # but must *always* include these fields:
    state = {
        "playerAmount" : 0,
        "playerNames" : [],
        "turnNr": 0
    }

    # this should only be written to by *this* class. It can be used
    # for lookup by subclasses, but *no* writing
    playerData = {
        "players" : {}
    }

    # must also be filled by subclass
    def parsePacket(self, packet: str, uuid: UUID):
        raise NotImplementedError

    # hooks to be filled by subclasses
    def _onRegister(self):
        raise NotImplementedError