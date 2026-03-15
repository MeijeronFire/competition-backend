# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from connections import ConnectionMgr
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
		#
		#
		#  THIS IS AN UGLY HACK
		#
		#
		super(Console, self).__init__()
		self.queue = queue
		self.loop = loop
		#
		#
		# THIS IS AN UGLY HACK
		#
		#

	# def do_hello(self, arg):
	# 	"""
	# 	usage: hello <name>

	# 	name: person to greet
	# 	"""
	# 	print(f"Hello {arg}")
	
	# def do_printstate(self, arg):
	# 	"""
	# 	usage: printstate
		
	# 	prints current state of game
	# 	"""
	# 	pprint(self.uber.state)
	
	# def do_printplayerdata(self, arg):
	# 	"""
	# 	usage: printstate
		
	# 	prints current state of game
	# 	"""
	# 	pprint(self.uber.playerData)

	# def do_kick(self, uuid: str):
	# 	"""
	# 	usage: kick <uuid>

	# 	kicks a player by a UUID
	# 	"""
	# 	name = self.uber.playerData["players"][uuid]["displayName"]
	# 	print(f"kicking {name}")
	# 	if self.uber.delPlayer(uuid):
	# 		print("succes")
	# 	else:
	# 		print('failure')
	
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