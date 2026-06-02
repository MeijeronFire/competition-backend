# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response

# for our HTTP routing
from app.auth.session import isAuthenticated
from app.auth.crypt import generateCsrf, validateCsrf

# for the form models
from app.models.verify import LoginForm
from app.models.datastructs import StateModel

from typing import Annotated, cast

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# HTML endpoint
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Route for the home page

    This route checks whether or not the user is logged in, and if so
    returns the "home.html" jinja2 template (with some initial values
    to make the JS rendering smoother)

    Args:
        request (Request): The request object describing the app and client

    Returns:
        Login (RedirectResponse):
            Redirects to /login if not authenticated
        Home (TemplateResponse):
            Renders "home.html"
    """
    state = cast(StateModel, request.app.state)
    if not isAuthenticated(request):
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    # logic if logged in
    request.session["csrf"] = generateCsrf()
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "cards": state.rMgr.buildState(),
            "csrf": request.session["csrf"],
            "gameNames": state.rMgr.games.keys(),
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Route for the login page

    Args:
        request (Request): The request object describing the app and client

    Returns:
        Login (Response):
            The login page containing the HTML together with a CSRF token and
            errors if the user has made previous login attempts
    """
    # if already logged in
    if isAuthenticated(request):
        return RedirectResponse(url=request.url_for("home"))
    # now we have to find a way to actually log in
    # first we store the csrf token
    request.session["csrf"] = generateCsrf()
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "csrf": request.session["csrf"],
            "errors": request.session.get("errors"),
        },
    )


@router.get("/peek/{roomID}")
async def peek(request: Request, roomID: int) -> Response:
    """Route for peeking at rooms

    Args:
        request (Request): The request object describing the app and client
        roomID (int): The ID of the room the user wants to view

    Returns:
        Login (RedirectResponse):
            If the user is nog logged in, we rederict to login

        Not found (TemplateResponse):
            If the `roomID` is unknown, we respond with `page_not_found.html` and
            tell the user that it does now exist

        Peek (TemplateResponse):
            If all is well, we send a GET response with the HTML of `peek.html`.
    """
    state = cast(StateModel, request.app.state)
    if not isAuthenticated(request):
        return RedirectResponse(url=request.url_for("login"))

    # logic if logged in
    # first we have to see if the room exists
    if roomID not in state.rMgr.rooms.keys():
        return templates.TemplateResponse(
            "page_not_found.html",
            {"request": request, "msg": "requested room ID does not exist."},
        )
    request.session["csrf"] = generateCsrf()
    return templates.TemplateResponse(
        "peek.html",
        {"request": request, "csrf": request.session["csrf"], "roomID": roomID},
    )
