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

# packet verification
from pydantic import ValidationError

# admin commands
from app import console

# self written modules
from app.connections import ConnectionMgr
from app.client import Client
from app.verify import *
from game.uber import Uber



game = Uber()
cmdQueue = asyncio.Queue()
connectionMgr = ConnectionMgr()

# TMP, DELETE ASAP
def readMsg(msg: dict) -> dict | None:
	msgType = msg["type"]
	match msgType:
		case "register":
			# register player in game state and capture UUID
			# acknowledge and share generated UUID of player
			pass
		
		case "getState":
			sleep(2)
			return {
				"type": "stateResp",
				"state": game.getState()
			}
		
		case "showPacket":
			sleep(2)
			return msg
		
		case "action":
			# we come up with our [resp]onse
			resp = game.handleAction(msg)
			if type(resp) == str:
				return {
					"type": resp
				}
			else:
				# thus it is a bool
				# if it is true we are done so we don't have to
				# respond with anything. If it is false we also
				# don't respond with anything, thus we just pass.
				pass
			return
		
		case _:
			return {
				"type": "error",
				"errorType": "unknown protocol"
			}


ALLOWED_ACTIONS = game.ALLOWED_ACTIONS + ["register"]

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
	task = asyncio.create_task(console.handler(game, cmdQueue, connectionMgr))
	task.add_done_callback(log_async_error)

	yield
	
	# after
	if task:
		task.cancel()

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# initialize client
async def initClient(ws: WebSocket):
	# accept the connection
	await ws.accept()

	# initialize the client object
	thisUser = Client(ws)

	# add this client to the list of connections
	connectionMgr.connect(ws, thisUser)
	return thisUser

# remove client
async def delClient(client: Client):
	# close the connection
	ws = client.ws
	await ws.close()

	# delete it from known connections
	connectionMgr.disconnect(ws)

	# remove the class
	del client
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
			"players" : game.state["playerNames"]
		})

# TRANSPORT LAYER
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
	connectedUser = await initClient(ws)
	# interpret the first packet, which contains
	# client-defined information
	data = await ws.receive_json()
	try:
		msg = json.loads(data)
	except json.JSONDecodeError:
		print(f"client {connectedUser} sent a malformed first packet.")
		await ws.close()
		return

	# so the registration contains correct json
	try:
		regPacket = RegisterPacket.model_validate(msg)
	except ValidationError:
		print(f"client {connectedUser} set an incorrect JSON registration packet.")
		await ws.close()
		return
	
	# do this until the websocket disconnects unexpectedly
	try: 
		while 1:
			data = await ws.receive_text()
			try: # do this unless the json is broken
				# read and load message
				msg = json.loads(data)
			except json.JSONDecodeError: # if the json is broken
				continue # wait for the next thingie

			resp = readMsg(msg) # handle the message
			await ws.send_json(resp) # send response
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
