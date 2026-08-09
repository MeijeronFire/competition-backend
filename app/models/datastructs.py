import asyncio
from typing import Any

# from uuid import UUID

from app.core import RoomManager, ConnectionMgr, GameSupervisor, Sender
from app.core.outbox import AdminStream


class StateModel:
    """State Model

    This class models the state stored in `app.state`, so that typehinting
    becomes possible.
    """

    rMgr: RoomManager
    cMgr: ConnectionMgr
    supervisor: GameSupervisor
    sender: Sender
    adminStream: AdminStream
    running: bool
    outbox: asyncio.Queue[tuple[str, dict[str, Any]]]
