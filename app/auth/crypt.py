# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import secrets


def generate_csrf():
    return secrets.token_urlsafe(32)
