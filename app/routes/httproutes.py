# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse

# for our HTTP routing
from app.auth.session import is_authenticated
from app.auth.crypt import generate_csrf, validate_csrf, is_user, validate_password

# for the form models
from app.models.verify import LoginForm
from app.models.primitives import StateModel

from typing import Annotated, cast

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# HTML endpoint
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    state = cast(StateModel, request.app.state)
    if not is_authenticated(request):
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    # logic if logged in
    request.session["csrf"] = generate_csrf()
    return templates.TemplateResponse("home.html", {
        "request": request,
        "rooms": [state.rMgr.rooms[i] for i in state.rMgr.rooms.keys()],
        "csrf": request.session["csrf"],
        "gameNames": state.rMgr.games.keys()
    })
    # return "Raaaah"


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # if already logged in
    if is_authenticated(request):
        return RedirectResponse(url=request.url_for("home"))
    # now we have to find a way to actually log in
    # first we store the csrf token
    request.session["csrf"] = generate_csrf()
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

    if not validate_csrf(request, data.csrf):
        errors["csrf"] = "Invalid session. Try login again."

    if not is_user(data.username):
        errors["username"] = "Username does not exist"
    elif not validate_password(data.username, data.password):
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
    if not validate_csrf(request, csrf):
        print("here")
        return RedirectResponse(url=request.url_for("home"), status_code=303)
    # if it is correct -> we clear everything
    print("here")
    request.session.clear()
    return RedirectResponse(url=request.url_for("login"), status_code=303)


@router.get("/dashboard")
async def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url=request.url_for("login"), status_code=303)
    return {"user": request.session["user"]}

# to allow anyone to see the icon, not that important


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
