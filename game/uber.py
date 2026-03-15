# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from .game import Game
from random import randint

"""
Woop woop game layer
"""

class Uber(Game):
    # not neccesary for the code, but good for reiterating the layout
    def __init__(self):
        self.state = {
            "playerAmount" : 0,
            "playerNames" : [],
            "turnNr": 0,
            "playerState" : {
                # to be filled like 'player': ml, ...
            },
            "glasses" : [0, 0, 0, 0, 0, 0],
            "optout": 300
        }
        self.waitingForFillAmount = False
        self.glassToBeFilled = 0

    def _onRegister(self):
        # add most recently added playername 
        recentName = self.state['playerNames'][-1]
        self.state["playerState"][recentName] = 0
    
    def incrementTurn(self):
        self.state["turnNr"] += 1

    def throw(self) -> int:
        return randint(0, 5) # like throwing a 0-indexed die
    
    def isEmpty(self, glassNr: int) -> bool:
        if self.state["glasses"][glassNr] == 0:
            return True
        else:
            return False

    def fill(self, glassNr: int, amount: int):
        self.state['glasses'][glassNr] = amount
        self.incrementTurn()
    
    def drink(self, playerName: str, glassNr: int):
        self.state['playerState'][playerName] += self.state['glasses'][glassNr]
        self.state['glasses'][glassNr] = 0
    
    def optOut(self, playerName):
        self.state['playerState'][playerName] += self.state['optout']
        self.incrementTurn()

    def handleAction(self, msg: dict) -> str | bool:
        """
        Docstring for handleAction
        
        :param msg: takes action packet from server (!!!CHANGE LATER!!!)
        :type msg: dict
        :return: returns false if player is not allowed to make the move, 
            true if the player is done and the next round can commence, or a
            str which will be sent back if the player needs to do some 
            further action
        :rtype: dict[Any, Any] | bool
        """
        # if it is not allowed in the first place
        if not self.isAllowed(msg):
            print("error in validating user packet!")
            return False

        move = msg["action"]["choice"]
        name = msg["name"]

        if move == "fillAmount" and self.waitingForFillAmount:
            # UNSAFE: although specified, we do not know for certain
            # that the client has included the field "fillAmount"
            self.fill(self.glassToBeFilled, msg["action"]["amount"])
            # If you fill it, you landed on an empty glass, so next turn
            return True

        if move == "optOut":
            self.optOut(name)
            return True
        
        if move == "throw" or move == "fillAmount":
            # so the player has thrown a die
            selected = self.throw()
            if self.isEmpty(selected):
                self.waitingForFillAmount = True
                self.glassToBeFilled = selected
                return "requestFillAmount"
            else:
                self.drink(name, selected)
                # ugly hack. Just set the turn number to one less
                # so the next turn will be for the same player
                # and return true asif a new round can start
                # self.state["turnNr"] -= 1 # this is broken. Fix
                return "throwAgain"
        
        # so we have not had a known action entered. Thus
        # we must assume the message is malformed and return false
        print("???")
        return False
        