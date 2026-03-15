# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford


from typing import Any
import uuid

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

    def isPlayer(self, uuid: str, name: str) -> bool:
        if not (uuid in self.playerData["players"]):
            return False
        
        if not (name == self.playerData["players"][uuid]["displayName"]):
            return False
        
        if not (name in self.state["playerNames"]):
            return False

        return True

    def genPlayer(self, name: str) -> bool | str:
        """
        genPlayer: safe interface for adding to the players in the
        state of the game
        
        :return: Returns false if it has failed, uuid of player 
        generated on succes.
        :rtype: bool | int
        """
        if name in self.state["playerNames"]:
            print(f"{name} is already mentioned!")
            return False

        self.state["playerNames"].append(name)

        
        # add entry of player id in playerstate thingie
        player_uuid = str(uuid.uuid4())
        self.playerData['players'][player_uuid] = {
            'playerNum' : self.state["playerAmount"],
            'displayName': name
        }
        self.state["playerAmount"] += 1 # increment the amount of players
        
        # optional call to be filled by further subclasses
        self._onRegister()
        return player_uuid

    def delPlayer(self, uuid: str) -> bool:
        """
        delPlayer: interface to delete players that have disconnected
        completely.
        
        :rtype: None
        """
        
        # first find the playername mapped to the uuid. Names are also
        # unique, but we don't want to be able to delete players by
        # using a publicly available key, for if we want to use this
        # as an interface for deregistering or smth. Best practice idk

        if uuid not in self.playerData["players"]:
            return False
        name = self.playerData["players"][uuid]['displayName']
        self.playerData["players"].pop(uuid)
        self.state["playerNames"].remove(name)
        self.state["playerAmount"] -= 1
        return True

    def getState(self) -> dict:
        return self.state

    def turn(self) -> str | None:
        if len(self.state["playerNames"]) == 0:
            return None
        name = self.state["playerNames"][self.state["turnNr"] % len(self.state["playerNames"])]
        # print(f"turn: {name}")
        return name

    def isAllowed(self, msg: dict) -> bool:
        """
        Returns true if the player has sufficient perms
        and it is his turn
        
        :return: returns true if holds
        :rtype: bool
        """
        uuid = msg["uuid"]
        name = msg["name"]
        turnName = self.state["playerNames"][self.state["turnNr"] % len(self.state["playerNames"])]
        if not self.isPlayer(uuid, name):
            return False
        if name != turnName:
            return False
        return True

    # must also be filled by subclass
    def handleAction(self, msg: dict):
        raise NotImplementedError

    # hooks to be filled by subclasses
    def _onRegister(self):
        raise NotImplementedError