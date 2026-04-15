# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford
from fastapi import WebSocket

from app.client import Client
from app.connections import ConnectionMgr

class gameHandler():
    def __init__(self, mgr: ConnectionMgr):
        pass