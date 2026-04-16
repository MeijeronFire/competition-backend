from contextlib import asynccontextmanager
import asyncio
import traceback
from fastapi import FastAPI
import threading

async def connectionMaster(game, mgr):
	await game.start()
	while True:
		await asyncio.sleep(0.1)
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

cmdQueue = asyncio.Queue()

@asynccontextmanager
async def lifespan(app: FastAPI):
	global loop
	loop = asyncio.get_running_loop()
	threading.Thread(target=console_runner, daemon=True).start()

	masterTask = asyncio.create_task(connectionMaster(app))
	masterTask.add_done_callback(log_async_error)

	yield
	
	# after
	if consoleTask:
		consoleTask.cancel()
	if masterTask:
		masterTask.cancel()