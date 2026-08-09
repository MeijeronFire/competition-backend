# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import hashlib
import json
import secrets
from fastapi.requests import Request
import csv

from fastapi import Request, WebSocket
from typing import Any, Union

import logging

_Connection = Union[Request, WebSocket]

logger = logging.getLogger(__name__)


def generateCsrf() -> str:
    """
    Generate a secure CSRF token.

    Returns:
        str: A URL-safe, cryptographically secure random token suitable for use as a CSRF token.
    """
    return secrets.token_urlsafe(32)


def validateCsrf(connection: _Connection, manualToken: str | None = None) -> bool:
    """validate CSRF token

    This function looks at a request sent by a user and verifies if it matches
    with the token set by the server.

    It either compares the provided string with the known token, or looks at the
    http header for a token. If both are provided, manualToken is checked.

    Args:
        connection (Union[Request, WebSocket]):
            Stores true token and http header. Typed to allow function to handle
            .session.get("csrf") for both websocket and HTTP requests.
        manualToken (str):
            The token for the request to be validated against

    Returns:
        bool: Whether or not the request matches with the CSRF token provided
    """
    providedToken = (
        manualToken
        if manualToken is not None
        else connection.headers.get("X-CSRF-Token")
    )
    trueToken = connection.session.get("csrf")
    return providedToken == trueToken


# lookup if a user is in the csv file
def isUser(username: str) -> bool:
    """Is user

    This function looks up if a user exists in our "database" of users. Often we
    want to know if a user exists, but we don't want to look up any info about
    passwords or authentication, so that is what this function is for. When integrating
    this into a larger system, this function should be rewritten, but as of now it is
    just a placeholder with a simple .csv file as auth database.

    Args:
        username (str): Name of the user to be looked up

    Returns:
        bool: Whether or not the user exists
    """
    with open("users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return True
    return False


# lookup if a password is correct, assuming user exists
def validatePassword(username: str, password: str) -> bool:
    """Validate password

    This function looks a username up and sees if the password stored in the
    auth database matches up with the password provided. When integrating this into
    a larger system, this function should be rewritten, but as of now it is just a
    placeholder with a simple .csv file as auth database.

    Args:
        username (str): Name of the user to be looked up
        password (str): The password to check

    Returns:
        bool: Whether or not the provided password is correct
    """
    with open("users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return row["password"] == password
    raise Exception("Provided user does not exist!")


# a way to calculate the hash in a consistent way
def computeJSONHash(obj: dict[Any, Any]) -> str:
    """Compute hash of JSONified dict

    This is a standardized way to turn a dict into a JSON string, and afterwards
    hash the JSON string, such that the result is reproducible across different
    languages and platforms, so that comparisons of the hashes can be made.

    Args:
        obj (dict): The dict to be hashed

    Returns:
        str: The string representation of the sha256 hash
    """
    jsonString = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    # logger.info(jsonString)
    return hashlib.sha256(jsonString.encode()).hexdigest()
