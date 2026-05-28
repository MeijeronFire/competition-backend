from app.core import RoomManager, ConnectionMgr, GameSupervisor, Sender
from app.core.outbox import AdminSender


class StateModel:
    """State Model

    This class models the state stored in `app.state`, so that typehinting
    becomes possible.
    """

    rMgr: RoomManager
    cMgr: ConnectionMgr
    supervisor: GameSupervisor
    sender: Sender
    adminSender: AdminSender
