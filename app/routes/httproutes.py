# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse

# for our HTTP routing
from app.auth.session import isAuthenticated
from app.auth.crypt import generateCsrf, validateCsrf, isUser, validatePassword

# for the form models
from app.models.verify import LoginForm
from app.models.datastructs import StateModel

from typing import Annotated, cast

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# HTML endpoint
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    state = cast(StateModel, request.app.state)
    if not isAuthenticated(request):
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    # logic if logged in
    request.session["csrf"] = generateCsrf()
    return templates.TemplateResponse("home.html", {
        "request": request,
        "rooms": [state.rMgr.rooms[i] for i in state.rMgr.rooms.keys()],
        "csrf": request.session["csrf"],
        "gameNames": state.rMgr.games.keys()
    })


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # if already logged in
    if isAuthenticated(request):
        return RedirectResponse(url=request.url_for("home"))
    # now we have to find a way to actually log in
    # first we store the csrf token
    request.session["csrf"] = generateCsrf()
    return templates.TemplateResponse("login.html", {
        "request": request,
        "csrf": request.session["csrf"],
        "errors": request.session.get("errors")
    })


@router.post("/login", response_class=HTMLResponse)
async def loginForm(request: Request, data: Annotated[LoginForm, Form()]):
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
def logout(request: Request, csrf: Annotated[str, Form()]):
    # if the CSRF token is incorrect -> untrusted request
    if not validateCsrf(request, csrf):
        print("here")
        return RedirectResponse(url=request.url_for("home"), status_code=303)
    # if it is correct -> we clear everything
    print("here")
    request.session.clear()
    return RedirectResponse(url=request.url_for("login"), status_code=303)


@router.get("/peek/{roomID}")
async def peek(request: Request, roomID: int):
    state = cast(StateModel, request.app.state)
    if not isAuthenticated(request):
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    # logic if logged in
    # first we have to see if the room exists
    if roomID not in state.rMgr.rooms.keys():
        return templates.TemplateResponse("page_not_found.html", {
            "request": request,
            "msg": "requested room ID does not exist."
        })
    request.session["csrf"] = generateCsrf()
    return templates.TemplateResponse("peek.html", {
        "request": request,
        "csrf": request.session["csrf"],
        "roomID": roomID
    })

# to allow anyone to see the icon, not that important


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
