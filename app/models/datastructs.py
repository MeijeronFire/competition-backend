from app.core import (
    RoomManager,
    ConnectionMgr,
    GameSupervisor,
    Sender
)


class StateModel:
    rMgr: RoomManager
    cMgr: ConnectionMgr
    supervisor: GameSupervisor
    sender: Sender
