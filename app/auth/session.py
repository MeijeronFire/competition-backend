# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import Request, WebSocket
from typing import Union

_Connection = Union[Request, WebSocket]


def getCurrentUser(request: _Connection) -> str:
    """Get username associated with request

    Args:
        request (Union[Request, WebSocket]):
            The request that stores the session cookie

    Returns:
        str: The name of the user logged in
    """
    return request.user.get("user")


def isAuthenticated(connection: _Connection) -> bool:
    """Is the user authenticated

    This function checks if the user over some connection is currently authenticated,
    so is allowed to view priviliged content.

    Args:
        connection (Union[Request, WebSocket]):
            The connection that stores the session cookie

    Returns:
        bool: whether or not the user is authenticated
    """
    return "user" in connection.session
