# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from app.connections import ConnectionMgr
from game.uber import Game
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
	
	def do_test(self, arg):
		"""
		usage: kick <msg>
		
		prints <msg>
		"""
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("test", arg)),
			self.loop
		)

	def do_sendState(self, arg):
		"""
		usage: sendState
		
		broadcasts current state to all connected clients
		"""
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("sendState", arg)),
			self.loop
		)

	def do_printState(self, arg):
		"""
		usage: printState
		
		prints current gameState dict in console
		"""
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("printState", arg)),
			self.loop
		)

	def do_printConnections(self, arg):
		"""
		usage: Connections
		
		prints current connected clients
		"""
		asyncio.run_coroutine_threadsafe(
			self.queue.put(("printConnections", arg)),
			self.loop
		)
	
	def do_thousandRounds(self, arg):
		for i in range(0, 1000):
			sleep(0.05)
			self.do_sendState(None)

async def handler(game: Game, queue: asyncio.queues.Queue, mgr: ConnectionMgr):
	while True:
		cmd, arg = await queue.get()
		match cmd:
			case("sendState"):
				turn = game.turn()
				send_thing = {
					"type" : "gameState",
					"state": game.getState(),
					"turn": turn
				}
				await mgr.broadcast(send_thing)

			case("printState"):
				print(game.getState())

			case("printConnections"):
				print(mgr.connections)

			case _:
				raise NotImplementedError(f"Error: called {cmd} which is not implemented in the handler function")