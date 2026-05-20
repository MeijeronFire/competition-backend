# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from pydantic import BaseModel, ConfigDict


class BaseMessage(BaseModel):
    action: str
    model_config = ConfigDict(extra="allow")


class RegisterPacket(BaseMessage):
    action: str = "register"
    name: str


class LoginForm(BaseModel):
    username: str
    password: str
    csrf: str


class DashRegMsg(BaseModel):
    csrf: str


class DashCreateMsg(BaseModel):
    name: str


class DashUpdateMsg(BaseModel):
    pass


class DashDeleteMsg(BaseModel):
    roomID: int


class DashGetRoomStateMsg(BaseModel):
    roomID: int
