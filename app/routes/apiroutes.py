# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from typing import Literal, cast
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse

from app.auth.crypt import validateCsrf
from app.auth.session import isAuthenticated

# form validation
from app.models.datastructs import StateModel
from app.models.verify import DashCreateMsg, DashRoomPlayerOperation

router = APIRouter()


@router.post("/api/room-{roomID}/delRoom")
async def delroom(request: Request, roomID: int):
    """POST API endpoint for requesting the deletion of a room

    Args:
        request (Request): The request object describing the app and client
        roomID (int): The ID of the room to delete

    Returns:
        400: HTTPException if CSRF token is incorrect
        401: HTTPException if user is not authenticated
        404: HTTPException if room does not exist
    """
    state = cast(StateModel, request.app.state)

    if not isAuthenticated(request):
        raise HTTPException(401, "Not authenticated. Operation not permitted.")

    if not validateCsrf(request):
        raise HTTPException(400, "CSRF token incorrect, operation not allowed.")

    if roomID not in state.rMgr.rooms:
        raise HTTPException(404, "Requested room does not exist.")

    # so we are allowed to do it
    await state.supervisor.delete(roomID)

    return Response(status_code=200)


@router.post("/api/createRoom")
async def createRoom(request: Request, msg: DashCreateMsg):
    """POST API endpoint for requesting the creation of a room

    Args:
        request (Request): The request object describing the app and client

    Returns:
        Response (200): If the creation is succesfull

    Raises:
        400: HTTPException if CSRF token is incorrect
        401: HTTPException if user is not authenticated
    """
    state = cast(StateModel, request.app.state)

    if not isAuthenticated(request):
        raise HTTPException(401, "Not authenticated. Operation not permitted.")

    if not validateCsrf(request):
        raise HTTPException(400, "CSRF token incorrect, operation not allowed.")

    if msg.gameName not in state.rMgr.games:
        raise HTTPException(404, "Requested game does not exist.")

    # so we are allowed to do it
    await state.supervisor.create(msg.gameName)

    return Response(status_code=200)


@router.post("/api/room-{roomID}/state-{operation}")
async def roomStateOperation(
    request: Request,
    roomID: int,
    operation: Literal["start", "stop", "open", "close", "reset"],
):
    """POST API endpoint for changing the room state @ roomID

    Note that starting the room closes new players from joining and locks
    existing players, i.e. throws an error if players leave.

    Since there are no actual arguments required other than the ID of the
    room to be started, it can be empty.

    Also note that this refers specifically to the room state, not the game
    state.

    Args:
        request (Request): The request object describing the app and client
        roomID (int): The room to which the request pertains
        operation (string): The operation to perform

    Raises:
        401 (HTTPException): If not authenticated
        400 (HTTPException): If CSRF token is incorrect, so operation not allowed
        404 (HTTPException): If requested room does not exist
    """
    state = cast(StateModel, request.app.state)

    if not isAuthenticated(request):
        raise HTTPException(401, "Not authenticated. Operation not permitted.")

    if not validateCsrf(request):
        raise HTTPException(400, "CSRF token incorrect, operation not allowed.")

    if roomID not in state.rMgr.rooms:
        raise HTTPException(404, "Requested game does not exist.")

    state.rMgr.rooms[roomID].setGame(operation)


@router.post("/api/room-{roomID}/playerOperation")
async def roomPlayerOperation(
    request: Request, roomID: int, msg: DashRoomPlayerOperation
):
    """POST API endpoint for changing players connected to room

    The supported operations are: kicking

    TODO:
        implement banning players
        make this interact with client objects rather than be just room specific

    Args:
        request (Request): The request object describing the app and client
        msg (DashCreateMsg): The pydantic form sent
        roomID (int): The room to which the request pertains

    Raises:
        401 (HTTPException): If not authenticated
        400 (HTTPException): If CSRF token is incorrect, so operation not allowed
        404 (HTTPException): If requested room does not exist
    """
    state = cast(StateModel, request.app.state)

    if not isAuthenticated(request):
        raise HTTPException(401, "Not authenticated. Operation not permitted.")

    if not validateCsrf(request):
        raise HTTPException(400, "CSRF token incorrect, operation not allowed.")

    if roomID not in state.rMgr.rooms:
        raise HTTPException(404, "Requested game does not exist.")

    # first we parse the incoming message
    if msg.action == "kick":
        # TODO: maybe move the disconnect responsibility to the supervisor
        await state.cMgr.disconnect(UUID(msg.targetPlayerUUID))

        await state.supervisor.kick(roomID, UUID(msg.targetPlayerUUID))
    else:
        raise NotImplementedError


# to allow anyone to see the icon, not that important
@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """favicon

    Using this explicit endpoint allows us to specify and acess the favicon anywhere.

    Returns:
        favicon (FileResponse): the favicon.ico file
    """
    return FileResponse("static/favicon.ico")
