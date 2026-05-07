# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi.requests import Request


def get_current_user(request: Request):
    """
    If user is not logged in, return None
    """
    return request.user.get("user")


def is_authenticated(request: Request):
    return "user" in request.session
