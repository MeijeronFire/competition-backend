# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from app.core.connections import ConnectionMgr
from game.games import Uber
from pprint import pprint
import cmd
import asyncio
from time import sleep

class Console(cmd.Cmd):
	intro = "Console intro"
	prompt = "[anker] - "
	def __init__(
			self,
			queue: asyncio.Queue,
			loop: asyncio.AbstractEventLoop
    ):
		super(Console, self).__init__()
		self.queue = queue
		self.loop = loop
	

	def do_printConnections(self, arg):
		"""
		usage: Connections
		
		prints current connected clients
		"""
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("printConnections", arg)),
			self.loop
		)
	
	def do_getState(self, arg):
		"""
		usage: getState
		
		prints current gamestate
		"""
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("getState", arg)),
			self.loop
		)

	def do_oneTurn(self, arg):
		"""
		usage: broadcast <message>
		
		send <message> to all connected clients.
		"""
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("oneTurn", arg)),
			self.loop
		)
	def do_oneFill(self, arg):
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("oneFill", arg)),
			self.loop
		)
	def do_points(self, arg):
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("points", arg)),
			self.loop
		)

async def handler(game: Uber, queue: asyncio.queues.Queue, mgr: ConnectionMgr):
	while True:
		cmd, arg = await queue.get()
		match cmd:
			case("printConnections"):
				print(mgr.connections)
			case("points"):
				print(game.playerNames)
				print(game.points)
			case("oneTurn"):
				await next(iter(mgr.connections)).send_json({"type": "turn"})
				# raise NotImplementedError
			case("oneFill"):
				await next(iter(mgr.connections)).send_json({"type": "fillAmount"})
			case("getState"):
				print(game.glasses)
			case _:
				raise NotImplementedError(f"Error: called {cmd} which is not implemented in the handler function")