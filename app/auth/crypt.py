# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import secrets
from fastapi.requests import Request
import csv

from fastapi import Request, WebSocket
from typing import Union

_Connection = Union[Request, WebSocket]


def generate_csrf():
    return secrets.token_urlsafe(32)


def validate_csrf(connection: _Connection, csrf_token: str) -> bool:
    csrf = connection.session.get("csrf")
    if not csrf or csrf != csrf_token:
        return False
    return True


# lookup if a user is in the csv file
def is_user(username: str) -> bool:
    with open("users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return True
    return False


# lookup if a password is correct, assuming user exists
def validate_password(username: str, password: str) -> bool:
    with open("users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return row["password"] == password
    raise Exception("Provided user does not exist!")
