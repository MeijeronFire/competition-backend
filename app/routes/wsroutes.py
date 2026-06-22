# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from json import JSONDecodeError

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.connections import initClient
from game.gameActor import GameActor
from app.models.verify import GameRegisterMsg, DashRegMsg
from app.models.datastructs import StateModel
from app.auth.session import isAuthenticated
from app.auth.crypt import validateCsrf
from pydantic import ValidationError, model_validator
from typing import cast

router = APIRouter()


@router.websocket("/ws/{roomID}")
async def websocket_endpoint(ws: WebSocket, roomID: int):
    """Room websocket connection endpoint

    This function serves as the primary interface for players connected to
    the server. Tht means that it is responsible for verification,
    registration, object construction, appending the player to other objects
    (and deleting them afterward) and of course handling incoming messages.

    This implies that our registration protocol for games is implemented in the
    below function. The code is not too obtuse, so for a more detailed view
    of how the registration protocol works, reading the source is reccomended.

    To seperate responsibility just a little bit, it does _not_ do any
    preprocessing for incoming messages. That means other code is responsible
    for handling issues like XSS protection or malformed JSON.

    TODO:
        Untangle a bit of this registration code

    Forwarding:
        After verification, all incoming messages are
        forwarded like here:
        `room.inbox.put((connectedUser.uuid, data))`
        If either of these arguments are not present, the message is ignored.


    Args:
        ws (WebSocket): WebSocket connection with the client
        roomID (int): ID of the room the client wants to connect to

    Returns:
        Error (JSON): A malformed `GameRegisterMsg` msg was sent
        Error (JSON): The provided `roomID` does not exist
        None (None): The websocket connection closed

    """
    state = cast(StateModel, ws.app.state)
    # after this point, never access the websocket object directly
    connectedUser = await initClient(ws)
    state.cMgr.connect(connectedUser)
    # interpret the first packet, which contains
    # client-defined information
    msg = await connectedUser.ws.receive_json()

    try:
        regPacket = GameRegisterMsg.model_validate(msg)
    except ValidationError:
        # TODO: name is incorrect. Instantly find name of client when registering
        print(f"client {connectedUser} sent an incorrect JSON registration packet.")
        # TODO: make this more verbose to explain which packet would be expected
        print(f"sending error to {ws.client}")
        await ws.send_json(
            {"type": "error", "errorType": "Incorrect JSON registration packet sent"}
        )
        await ws.close()
        return

    # now we see if the specified room indeed exists
    try:
        room = state.rMgr.rooms[roomID]
    except KeyError, ValueError:
        print(f"client {connectedUser} sent an incorrect JSON registration packet.")
        # TODO: make this more verbose to explain the room is incorrect
        await ws.send_json(
            {"type": "error", "errorType": "Incorrect JSON registration packet sent"}
        )
        await ws.close()
        return

    # now we know we have a correct JSON packet so we can start interpreting the connection
    connectedUser.uname(regPacket.name)
    # add this client to the list of players
    try:
        await room.addPlayer(connectedUser.uuid, regPacket.name)
        # MAKE THIS CONDITIONAL
        # which function to execute when the user receives a packet

        # we send a response to the user
        await ws.send_json({"type": "regResp", "msg": "Registration OK."})

        # do this until the websocket disconnects unexpectedly
        while True:
            try:
                data = await ws.receive_json()
            except JSONDecodeError:
                continue
            # print(f"We got data: {data}")
            await room.inbox.put((connectedUser.uuid, data))
    except WebSocketDisconnect:
        # on disconnect run the manager disconnect hook
        # delete it from known connections
        await state.cMgr.disconnect(connectedUser.uuid)
        # inform room that the user does not exist any longer
        await room.popPlayer(connectedUser.uuid)
        return
