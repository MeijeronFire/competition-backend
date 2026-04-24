# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import WebSocket
import asyncio
from uuid import uuid4, UUID

# initialize client
async def initClient(ws: WebSocket) -> Client:
	# accept the connection
	await ws.accept()

	# initialize the client object
	thisUser = Client(ws)

	return thisUser

# remove client
async def delClient(client: Client):
	# close the connection
	ws = client.ws
	await ws.close()

	return

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

class ConnectionMgr:
    def __init__(self):
        # list of connections - should be live ones
        self.connections: dict[WebSocket, Client] = {}
        # client by UUID
        self.clients: dict[UUID, Client] = {}
        self.connectionlock = False
    
    def connect(self, client: Client):
        # don't allow further connection if it has been locked
        if self.connectionlock:
            print("Connection changes have been locked. Game must stop!")
            exit(0)
        # safe .append
        self.connections[client.ws] = client
        self.clients[client.uuid] = client

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
