# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
from app.client import Client
import asyncio

class ConnectionMgr:
    def __init__(self):
        # list of connections - should be live ones
        self.connections: dict[WebSocket, Client] = {}
        self.connectionlock = False
    
    def connect(self, ws: WebSocket, client: Client):
        # don't allow further connection if it has been locked
        if self.connectionlock:
            print("Connection changes have been locked. Game must stop!")
            exit(0)
        # safe .append
        self.connections[ws] = client
    
    def disconnect(self, ws):
        # safe .remove method
        self.connections.pop(ws)
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

        async def send(ws: WebSocket):
            try:
                print(f"connections.py: broadcasted to {self.connections[ws].userName}.")
                await ws.send_json(msg)
            except Exception:
                dead.append(ws)
        
        await asyncio.gather(*(send(ws) for ws in connections))

        for ws in dead:
            self.disconnect(ws)
