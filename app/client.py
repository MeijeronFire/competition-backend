# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from uuid import uuid4

class Client():
    def __init__(self, ws: WebSocket):
        self.uuid = str(uuid4())
        self.userName = self.uuid
        self.ws = ws
    
    def uname(self, username: str):
        self.userName = username
    
    def __str__(self) -> str:
        return self.userName