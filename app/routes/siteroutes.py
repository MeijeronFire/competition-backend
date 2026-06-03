# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response

# for our HTTP routing
from app.auth.session import isAuthenticated
from app.auth.crypt import generateCsrf, isUser, validateCsrf, validatePassword

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
        {
            "request": request,
            "csrf": request.session["csrf"],
            "roomID": roomID,
            "initialJSON": dict(
                [
                    (
                        str(uuid),
                        {
                            "name": state.rMgr.rooms[roomID].game.playerNames[uuid],
                            "UUID": str(uuid),
                        },
                    )
                    for uuid in state.rMgr.rooms[roomID].game.UUIDs
                ]
            ),
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def loginForm(
    request: Request, data: Annotated[LoginForm, Form()]
) -> RedirectResponse:
    """POST API endpoint for login attempts

    Args:
        request (Request): The request object describing the app and client
        data (Annotated[LoginForm, Form]): The form the user filled in

    Returns:
        Error (HTTPException):
            If the user is already logged in, he should not be sending any message,
            so a code 400 is raised and sent

        Home (Redirect):
            If the user provides correct credentials, matches the CSRF token,
            and is not logged in, they are redirected to "home" and we remember
            that the user is logged in.

        Login (RedirectResponse):
            If the user does not provide correct credentials, they are sent back to
            home and we update the errors with the login attempt.
    """
    # we should not even consider this if the user is already logged in
    if isAuthenticated(request):
        # 303 code because we are on a POST endpoint
        raise HTTPException(status_code=400, detail="Already logged in.")

    # first clear existing errors
    request.session["errors"] = None
    # first we check if the csrf tokens are correct
    errors: dict[str, str] = {}

    if not validateCsrf(request, data.csrf):
        errors["csrf"] = "Invalid session. Try login again."

    if not isUser(data.username):
        errors["username"] = "Username does not exist"
    elif not validatePassword(data.username, data.password):
        errors["password"] = "Password is not correct!"

    if errors:
        request.session["errors"] = errors
        return RedirectResponse(request.url_for("login"), status_code=303)

    print("Login OK!")
    request.session["user"] = data.username
    return RedirectResponse(url=request.url_for("home"), status_code=303)


@router.post("/logout")
def logout(request: Request, csrf: Annotated[str, Form()]) -> RedirectResponse:
    """POST API endpoint for logout attempts

    Args:
        request (Request): The request object describing the app and client
        csrf (Annotated[str, Form]): A hidden form containing the CSRF token

    Returns:
        Home (HTTPException):
            If the user does not provide a valid CSRF token, we send back a 400 error
        Login (RedirectResponse)
            If the user provides the correct CSRF token, they are redirected to /login
    """
    # if the CSRF token is incorrect -> untrusted request
    if not validateCsrf(request, csrf):
        raise HTTPException(400, "CSRF token incorrect, operation not allowed.")
    # if it is correct -> we clear everything
    request.session.clear()
    return RedirectResponse(url=request.url_for("login"), status_code=303)
