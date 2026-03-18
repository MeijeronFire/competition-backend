# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from types import FunctionType
from uuid import uuid4

class Client():
    def __init__(self, ws: WebSocket):
        self.uuid = str(uuid4())
        self.userName = "FooBar"
        self.ws = ws
        self.handleMsg: FunctionType
    
    # set username of client
    def uname(self, username: str):
        self.userName = username
    
    def route(self, listener: FunctionType):
        self.handleMsg = listener
    
    def __str__(self) -> str:
        return self.userName