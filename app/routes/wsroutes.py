# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.connections import initClient
from game.gameActor import GameActor
from app.models.verify import RegisterPacket, DashRegMsg
from app.models.datastructs import StateModel
from app.auth.session import isAuthenticated
from app.auth.crypt import validateCsrf
from pydantic import ValidationError, model_validator
from typing import cast

router = APIRouter()

# iws = interface websocket


@router.websocket("/ws/dashboard")
async def dashboard(ws: WebSocket):
    state = cast(StateModel, ws.app.state)
    # step 0: accept connection
    connectedUser = await initClient(ws)

   # step 1: see if user is even allowed
    if not isAuthenticated(ws):
        await ws.close(1008)
        return

    # step 2: we see if there is csrf included in initial msg
    msg = await ws.receive_json()
    try:
        authMsg = DashRegMsg.model_validate(msg)
    except ValidationError:
        await ws.send_json({
            "type": "error",
            "errorType": "Sent malformed authentication packet. "
            'Expected {"csrf": [base64 token]} token, '
            f"got {msg}"
        })
        await ws.close()
        return

    # step 3: actually validate the csrf
    if not validateCsrf(ws, authMsg.csrf):
        await ws.send_json({
            "type": "error",
            "errorType": f"Invalid session. Retry after reloading the page."
        })
        # policy violation, auth failure
        await ws.close(1008)
        return

    # we can add the user to the list of players we know
    state.cMgr.connect(connectedUser)
    state.supervisor.admins.append(connectedUser.uuid)

    # Now we are in the clear and we can start parsing messages.
    # do this until the websocket disconnects unexpectedly
    # TODO: enclose the rest of the code in try as well!
    try:
        while True:
            msg = await ws.receive_json()
            if msg.get("action") is None or msg.get("data") is None:
                continue
            # await state.supervisorQueue.put((msg["action"], msg["data"]))
            await state.supervisor.parse(msg["action"], msg["data"])
    except WebSocketDisconnect:
        # on disconnect run this hook
        print(f"Disconnected {connectedUser.uuid}")
        # delete it from known connections
        state.cMgr.disconnect(connectedUser.uuid)
        state.supervisor.admins.remove(connectedUser.uuid)


@router.websocket("/ws/{roomID}")
async def websocket_endpoint(ws: WebSocket, roomID: int):
    state = cast(StateModel, ws.app.state)
    # after this point, never access the websocket object directly
    connectedUser = await initClient(ws)
    state.cMgr.connect(connectedUser)
    # interpret the first packet, which contains
    # client-defined information
    msg = await connectedUser.ws.receive_json()

    try:
        regPacket = RegisterPacket.model_validate(msg)
    except ValidationError:
        # TODO: name is incorrect. Instantly find name of client when registering
        print(
            f"client {connectedUser} sent an incorrect JSON registration packet.")
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
        room = state.rMgr.rooms[roomID]
    except (KeyError, ValueError):
        print(
            f"client {connectedUser} sent an incorrect JSON registration packet.")
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
            # print(f"We got data: {data}")
            await room.inbox.put((connectedUser.uuid, data))
    except WebSocketDisconnect:
        # on disconnect run the manager disconnect hook
        # delete it from known connections
        state.cMgr.disconnect(connectedUser.uuid)
        # inform room that the user does not exist any longer
        # room.game.delplayer(UUID) (?)
        return
