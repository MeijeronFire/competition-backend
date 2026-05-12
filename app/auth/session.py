# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import Request, WebSocket
from typing import Union

_Connection = Union[Request, WebSocket]


def getCurrentUser(request: Request):
    """
    If user is not logged in, return None
    """
    return request.user.get("user")


def isAuthenticated(connection: _Connection):
    return "user" in connection.session
