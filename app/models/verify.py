# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

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


class DashUpdateMsg(BaseModel):
    """Dashboard Update [room] Message

    TODO: the user does not yet have the option to change a room.

    This class models a change the user makes in a dashboard to how
    a game works, i.e. opening it, closing it, removing players,
    adding players, etc.


    Args:
        BaseModel (BaseModel): Inheritance
    """

    pass


class DashDeleteMsg(BaseModel):
    """Dashboard Delete [room] Message

    This class models the deletion request of an admin. It only
    requires the ID of the room that is to be deleted

    Args:
        BaseModel (BaseModel): Inheritance
    """

    roomID: int


class DashGetRoomStateMsg(BaseModel):
    """Dashboard Get Room State Message

    This class models the request to get the state of a given
    room. It only requires the ID of the room of which the state
    is requested.

    Args:
        BaseModel (BaseModel): Inheritance
    """

    roomID: int
