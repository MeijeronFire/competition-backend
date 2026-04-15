# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from typing import Callable, Generator, Tuple
from uuid import uuid4, UUID

class Client():
    def __init__(self, ws: WebSocket):
        self.uuid = uuid4()
        self.userName = "FooBar"
        self.ws = ws
    
    def route(self):
        pass

    # set username of client
    def uname(self, username: str):
        self.userName = username
    
    def __str__(self) -> str:
        return self.userName