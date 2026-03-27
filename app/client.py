# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from typing import Callable, Generator
from uuid import uuid4

class Client():
    def __init__(self, ws: WebSocket):
        self.uuid = uuid4()
        self.userName = "FooBar"
        self.ws = ws
        self._handler: Generator[dict, dict, None]
    
    def handleMsg(self, msg: dict):
        if self._handler == None:
            raise NotImplementedError("You have not specified the listener")
        return self._handler.send(msg)

    # set username of client
    def uname(self, username: str):
        self.userName = username
    
    def route(self, listener: Callable[[], Generator[dict, dict, None]]):
        # so we call the object to instantiate the generator :)
        self._handler = listener()
        # prime the handler, i.e. arrive at the first yield of the function
        next(self._handler)
    
    def __str__(self) -> str:
        return self.userName