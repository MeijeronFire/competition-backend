# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from typing import Callable
from uuid import uuid4

class Client():
    def __init__(self, ws: WebSocket):
        self.uuid = uuid4()
        self.userName = "FooBar"
        self.ws = ws
        self._listener: Callable
    
    def handleMsg(self, msg: str):
        if self._listener == None:
            raise NotImplementedError("You have not specified the listener")
        self._listener(msg, self.uuid)

    # set username of client
    def uname(self, username: str):
        self.userName = username
    
    def route(self, listener: Callable):
        self._listener = listener
    
    def __str__(self) -> str:
        return self.userName