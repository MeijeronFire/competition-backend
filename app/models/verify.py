# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from typing import Literal

from pydantic import BaseModel, ConfigDict


class BaseMessage(BaseModel):
    """Base message

    This class models a standard websocket message, containing only an action

    Args:
        BaseModel (BaseModel):
            Neccesary inheritance from pydantic
    """

    action: str
    model_config = ConfigDict(extra="allow")


class GameRegisterMsg(BaseMessage):
    """Game Register Message

    This class models what a registration message should look like. It is dependant on
    BaseMessage

    Args:
        BaseMessage (BaseMessage): Inheritance
    """

    action: str = "register"
    name: str


class LoginForm(BaseModel):
    """Login Form message

    Args:
        BaseModel (BaseModel):
            This class models what a LOGIN POST request looks like.
            It contains a username, as password and a CSRF token
    """

    username: str
    password: str
    csrf: str


class DashRegMsg(BaseModel):
    """Dashboard Register Message

    This class models a dashboard register message. It contains only a CSRF token
    that makes sure that the websocket connection is legitimate.

    Args:
        BaseModel (BaseModel):
            Inheritance
    """

    csrf: str


class DashCreateMsg(BaseModel):
    """Dashboard Create [room] Message

    This class models the creation of a new room from the dashboard.
    It only contains the field name, which is the name of the room to
    be created.

    Args:
        BaseModel (BaseModel): Inheritance
    """

    gameName: str


class DashRoomPlayerOperation(BaseModel):
    """Dashboard Room Player Operation

    Messages of this type model the changes a user can make to a player,
    currently kicking a player.

    Args:
        BaseModel (BaseModel): Inheritance
    """

    action: Literal["kick"]
    targetPlayerUUID: str
