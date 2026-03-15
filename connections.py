# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from typing import Set
import asyncio

class ConnectionMgr:
    def __init__(self):
        # list of connections - should be live ones
        self.connections: dict[str, WebSocket] = {}
        self.connectionlock = False
    
    async def connect(self, uuid: str, ws: WebSocket):
        # don't allow further connection if it has been locked
        if self.connectionlock:
            print("Connection changes have been locked. Game must stop!")
            exit(0)
        # safe .append
        self.connections[uuid] = ws
    
    async def throwError(self, ws: WebSocket):
        await ws.send_json({
            "type": "error",
            "errorType": "malformed json"
		})
        print(f"Incoming json had an error")

    def disconnect(self, uuid: str):
        # safe .remove method
        self.connections.pop(uuid)
        print("Client disconnected (normal or abnormal)")
        # we still want to get rid of the dead connection, 
        # so this is afterwards
        if self.connectionlock:
            print("connection changes have been locked. Game must stop!")
            exit(0)
    
    async def broadcast(self, msg: dict):
        # list of dead connections
        dead = []
        connections = self.connections

        async def send(uuid: str, ws: WebSocket):
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(uuid)
        
        await asyncio.gather(*(send(ws, connections[ws]) for ws in connections))

        for ws in dead:
            self.disconnect(ws)
