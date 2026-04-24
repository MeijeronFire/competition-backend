# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from contextlib import asynccontextmanager
import asyncio
import traceback
from fastapi import FastAPI
from typing import Tuple, Dict
from uuid import UUID

from game import Uber 

from app.core import Client
from app.core import ConnectionMgr
from app.core import RoomManager
from app.core import Sender

def log_async_error(task: asyncio.Task):
	try:
		task.result()
	except:
		traceback.print_exc()

async def gameSupervisor(app, rMgr: RoomManager):
	tasks: list[asyncio.Task] = []
	# uber = rMgr.create("uber")
	example = rMgr.create("example")
	# TODO: move the task creation to RoomManager rather than here
	tasks.append(asyncio.create_task(rMgr.rooms[example].run()))
	tasks[0].add_done_callback(log_async_error)

	while True:
		await asyncio.sleep(10)
		# print("slept for 10 seconds :)")

@asynccontextmanager
async def lifespan(app: FastAPI):
	# set the maxsize to 100, s.t. if the handling is less than traffic,
	# we block allowing new msgs
	# inbox: asyncio.Queue[Tuple[Client, Dict]] = asyncio.Queue(maxsize = 100)
	outbox: asyncio.Queue[Tuple[UUID, Dict]] = asyncio.Queue(maxsize=100)
	app.state.outbox = outbox
	rMgr = RoomManager(outbox)
	cMgr = ConnectionMgr()
	app.state.rMgr = rMgr
	app.state.cMgr = cMgr

	gameSupervisorTask = asyncio.create_task(gameSupervisor(app, rMgr))
	gameSupervisorTask.add_done_callback(log_async_error)

	# now we instantiate the sender postoffice!
	sender = Sender(outbox, cMgr)
	await sender.start()

	yield
	
	await sender.stop()

	if gameSupervisorTask:
		gameSupervisorTask.cancel()