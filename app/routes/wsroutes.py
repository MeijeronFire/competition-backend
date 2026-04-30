# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.connections import initClient, delClient
from app.core import RoomManager
from game.gameActor import GameActor
from app.models.verify import RegisterPacket
from pydantic import ValidationError

router = APIRouter()

# iws = interface websocket
@router.get("/ws/interface")
async def control_websocket(iws: WebSocket):
    pass

# TRANSPORT LAYER
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    # after this point, never access the websocket object directly
    connectedUser = await initClient(ws)
    ws.app.state.cMgr.connect(connectedUser)
    # interpret the first packet, which contains
    # client-defined information
    msg = await connectedUser.ws.receive_json()

    try:
        regPacket = RegisterPacket.model_validate(msg)
    except ValidationError:
        # TODO: name is incorrect. Instantly find name of client when registering
        print(f"client {connectedUser} set an incorrect JSON registration packet.")
        # TODO: make this more verbose to explain which packet would be expected
        print(f"sending error to {ws.client}")
        await ws.send_json({
            "type": "error",
            "errorType": "Incorrect JSON registration packet sent"
        })
        await ws.close()
        return

    # now we see if the specified room indeed exists
    try:
        room: GameActor = ws.app.state.rMgr.rooms[int(room_id)]
    except (KeyError, ValueError):
        print(f"client {connectedUser} set an incorrect JSON registration packet.")
        # TODO: make this more verbose to explain the room is incorrect
        await ws.send_json({
            "type": "error",
            "errorType": "Incorrect JSON registration packet sent"
        })
        await ws.close()
        return
    
    # now we know we have a correct JSON packet so we can start interpreting the connection
    connectedUser.uname(regPacket.name)
    # add this client to the list of players
    room.game.addPlayer(connectedUser.uuid, regPacket.name)
    # MAKE THIS CONDITIONAL
    # which function to execute when the user receives a packet

    # we send a response to the user
    await ws.send_json({
        "type": "regResp",
        "msg": "Registration OK."
    })

    # do this until the websocket disconnects unexpectedly
    try: 
        while True:
            data = await ws.receive_json()
            print(f"We got data: {data}")
            await room.inbox.put((connectedUser.uuid, data))
    except WebSocketDisconnect:
        # on disconnect run the manager disconnect hook
        await delClient(connectedUser)
        # delete it from known connections
        ws.app.state.cMgr.disconnect(ws)
        return
