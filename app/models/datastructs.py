from app.core import RoomManager, ConnectionMgr, GameSupervisor, Sender
from app.core.outbox import AdminSender


class StateModel:
    rMgr: RoomManager
    cMgr: ConnectionMgr
    supervisor: GameSupervisor
    sender: Sender
    adminSender: AdminSender
