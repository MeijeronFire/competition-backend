# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# actual server 
import uvicorn

# utils
import json
import threading
import asyncio
import traceback
from time import sleep
from typing import Tuple, Dict

# packet verification
from pydantic import ValidationError

# admin commands
from app import console

# self written modules
from app.connections import ConnectionMgr
from app.client import Client
from app.verify import *
from game.games import Uber



game = Uber()
cmdQueue = asyncio.Queue()
# set the maxsize to 100, s.t. if the handling is less than traffic,
# we block allowing new msgs
msgQueue: asyncio.Queue[Tuple[Client, Dict]] = asyncio.Queue(maxsize = 100)
mgr = ConnectionMgr()

async def connectionMaster():
	while True:
		await asyncio.sleep(3)
		if len(game.UUIDs) < 2:
			print(f"skipped. {len(game.UUIDs)} / 2")
			continue
		
		# the client object whos turn it is
		sentTo = mgr.clients[game.turnUUID()]
		# tell client it is his turn
		await sentTo.ws.send_json({
			"type": "turn"
		})
		while True:
			# until we get the message we want
			sender, msg = await msgQueue.get()
			if sender == sentTo:
				break
		
		resp = game.parseMessage(msg)
		if resp is not None:
			# thus it is a dict, game.parseMessage(dict) -> dict | None
			await sender.ws.send_json(resp)

# utils
def console_runner():
	try:
		console.Console(cmdQueue, loop).cmdloop()
	except Exception:
		traceback.print_exc()

def log_async_error(task: asyncio.Task):
	try:
		task.result()
	except:
		traceback.print_exc()

# program lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
	global loop
	loop = asyncio.get_running_loop()
	threading.Thread(target=console_runner, daemon=True).start()
	consoleTask = asyncio.create_task(console.handler(game, cmdQueue, mgr))
	consoleTask.add_done_callback(log_async_error)

	masterTask = asyncio.create_task(connectionMaster())
	masterTask.add_done_callback(log_async_error)

	yield
	
	# after
	if consoleTask:
		consoleTask.cancel()
	if masterTask:
		masterTask.cancel()

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# initialize client
async def initClient(ws: WebSocket) -> Client:
	# accept the connection
	await ws.accept()

	# initialize the client object
	thisUser = Client(ws)

	# add this client to the list of connections
	mgr.connect(ws, thisUser)

	# add this client to the list of players
	game.addPlayer(thisUser.uuid, thisUser.userName)
	return thisUser

# remove client
async def delClient(client: Client):
	# close the connection
	ws = client.ws
	await ws.close()

	# delete it from known connections
	mgr.disconnect(ws)

	return

#
# API endpoints
#

## HTML endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
	return templates.TemplateResponse("index.html", {
		"request": request,
		"title": "FastAPI Game",
		"players" : game.playerNames
	})

# TRANSPORT LAYER
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
	# after this point, never access the websocket object directly
	connectedUser = await initClient(ws)
	# interpret the first packet, which contains
	# client-defined information
	msg = await connectedUser.ws.receive_json()

	try:
		regPacket = RegisterPacket.model_validate(msg)
	except ValidationError:
		print(f"client {connectedUser} set an incorrect JSON registration packet.")
		# TODO: make this more verbose to explain which packet would be expected
		await ws.send_json({
			"type": "error",
			"errorType": "Incorrect JSON registration packet sent"
		})
		await ws.close()
		return
	
	# now we know we have a correct JSON packet so we can start interpreting the connection
	connectedUser.uname(regPacket.name)

	# MAKE THIS CONDITIONAL
	# which function to execute when the user receives a packet

	# we send a response to the user
	await ws.send_json({
		"type": "regResp",
		"msg": "Registration OK."
	})

	# do this until the websocket disconnects unexpectedly
	try: 
		while 1:
			data = await ws.receive_json()
			print(f"We got data: {data}")
			await msgQueue.put((connectedUser, data))
	except WebSocketDisconnect:
		# on disconnect run the manager disconnect hook
		await delClient(connectedUser)
		return

	# make sure msg contains all required fields

if __name__ == "__main__":
	uvicorn.run(
		app,
		host="127.0.0.1",
		port=8000,
	)
