from contextlib import asynccontextmanager
import asyncio
import traceback
from fastapi import FastAPI
from typing import Tuple, Dict

from game import Uber 

from app.core import Client
from app.core import ConnectionMgr

async def connectionMaster(game, mgr, msgQueue):
	await game.start()
	while True:
		await asyncio.sleep(2)
		if len(game.UUIDs) < 2:
			print(f"skipped. {len(game.UUIDs)} / 2")
			continue
		
		# the client object whos turn it is
		sentTo = mgr.clients[game.turnUUID()]
		# tell client it is his turn
		await sentTo.ws.send_json({
			"type": "turn",
			"state": game.glasses
		})
		while True:
			while True:
				# until we get the message we want
				sender, msg = await msgQueue.get()
				if sender == sentTo:
					break
			
			resp = await game.parseMessage(msg)
			if resp is None:
				break
			# thus it is a dict, game.parseMessage(dict) -> dict | None
			print(f"sending {resp} to {sender.userName}")
			await sender.ws.send_json(resp)

def log_async_error(task: asyncio.Task):
	try:
		task.result()
	except:
		traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
	game = Uber()
	# set the maxsize to 100, s.t. if the handling is less than traffic,
	# we block allowing new msgs
	msgQueue: asyncio.Queue[Tuple[Client, Dict]] = asyncio.Queue(maxsize = 100)
	mgr = ConnectionMgr()

	app.state.msgQueue = msgQueue
	app.state.mgr = mgr
	app.state.game = game

	masterTask = asyncio.create_task(connectionMaster(game, mgr, msgQueue))
	masterTask.add_done_callback(log_async_error)

	yield
	
	if masterTask:
		masterTask.cancel()