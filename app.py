# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

#####################################################################
"""
Accepted protocols:
	Every message must have a:
		- type
		- timestamp
		- own UUID for every request that is not _register_
		- personal name
	Specific queries:
	
	register: registers player
		input:
			name: displayname: (str)
		output:
			type: regResp
			uuid: UUID

	
	getState: returns the current state, i.e. game.state
		input:
		output:
	
	showPacket: returns the packet sent
		input
		output
	
	error: says there is an error

	gameState: shows the current state and who's turn it is
		data: {...} (the current state as defined by the game implemented)
		turn: displayname of the current player

"""
#####################################################################

#
# imports for server
#

# fastapi
from fastapi import FastAPI, WebSocket, Request
from fastapi import WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# admin commands
import console

# connection manager
from connections import ConnectionMgr

# game classes
from game.uber import Uber

# actual server 
import uvicorn

# utils
import json
import threading
import asyncio
import traceback
from time import sleep

#
# definitions
#

game = Uber()
cmdQueue = asyncio.Queue()
connectionMgr = ConnectionMgr()
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
	

# organize the lifecycle, i.e. before and after starting the app
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


#
# protocol layer
#

def startGame():
	connectionMgr.connectionlock = True
	raise NotImplementedError

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

app = FastAPI(lifespan=lifespan)
# load html and css from those folders
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
	# first wait for a register packet and
	# then simply load that player
	# UNSAFE UNSAFE UNSAFE UNSAFE
	await ws.accept()
	data = await ws.receive_text()
	msg = json.loads(data)
	uuid = game.genPlayer(msg["name"])
	if uuid == False:
		await ws.send_json({
			"type": "error",
			"errorType": "illegal name, already chosen"
		})
		await ws.close()
		return
	
	assert isinstance(uuid, str)
	await ws.send_json({
		"type": "regResp",
		'uuid': uuid
	})
	# UNSAFE UNSAFE UNSAFE
	# add incoming connection to list of connections
	await connectionMgr.connect(uuid, ws)

	try: # do this until the websocket disconnects unexpectedly
		while 1:	
			try: # do this unless the json is broken
				# read and load message
				data = await ws.receive_text()
				msg = json.loads(data)
			except json.JSONDecodeError: # if the json is broken
				continue # wait for the next thingie

			resp = readMsg(msg) # handle the message
			await ws.send_json(resp) # send response
	except WebSocketDisconnect:
		# on disconnect run the manager disconnect hook
		connectionMgr.disconnect(uuid)
		game.delPlayer(uuid)

if __name__ == "__main__":
	uvicorn.run(
		app,
		host="127.0.0.1",
		port=8000,
	)
