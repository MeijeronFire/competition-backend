# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import hashlib
import json
import secrets
from fastapi.requests import Request
import csv

from fastapi import Request, WebSocket
from typing import Union

_Connection = Union[Request, WebSocket]


def generateCsrf():
    return secrets.token_urlsafe(32)


def validateCsrf(connection: _Connection, csrf_token: str) -> bool:
    csrf = connection.session.get("csrf")
    if not csrf or csrf != csrf_token:
        return False
    return True


# lookup if a user is in the csv file
def isUser(username: str) -> bool:
    with open("users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return True
    return False


# lookup if a password is correct, assuming user exists
def validatePassword(username: str, password: str) -> bool:
    with open("users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return row["password"] == password
    raise Exception("Provided user does not exist!")


# a way to calculate the hash in a consistent way
def computeHash(obj):
    jsonString = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(jsonString.encode()).hexdigest()
