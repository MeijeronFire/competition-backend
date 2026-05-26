# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import logging
import asyncio
import traceback

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(filename)s:%(lineno)d "
        "%(message)s"
    ),
    datefmt="%H:%M:%S",
)


def log_async_error(task: asyncio.Task):
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        traceback.print_exc()
