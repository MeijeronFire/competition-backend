# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import FastAPI

# actual server 
import uvicorn

import asyncio
from time import sleep
from typing import Tuple, Dict

# self written modules
from app.core.connections import ConnectionMgr
from app.core.client import Client
from app.models.verify import *
from app.lifecycle import lifespan
from game.games import Uber

game = Uber()
# set the maxsize to 100, s.t. if the handling is less than traffic,
# we block allowing new msgs
msgQueue: asyncio.Queue[Tuple[Client, Dict]] = asyncio.Queue(maxsize = 100)
mgr = ConnectionMgr()

app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
	uvicorn.run(
		app,
		host="127.0.0.1",
		port=8000,
	)
