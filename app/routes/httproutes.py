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

from typing import Annotated

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# HTML endpoint
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    # logic if logged in
    request.session["csrf"] = generate_csrf()
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "FastAPI Game",
        "stats": request.app.state.rMgr,
        "csrf": request.session["csrf"]
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
        "errors": None
    })


@router.post("/login", response_class=HTMLResponse)
async def loginForm(request: Request, data: Annotated[LoginForm, Form()]):
    # first we check if the csrf tokens are correct
    errors: dict[str, str] = {}

    if not validate_csrf(request, data.csrf):
        errors["csrf"] = "Invalid session. Refresh the page"

    if not is_user(data.username):
        errors["username"] = "Username does not exist"
    elif not validate_password(data.username, data.password):
        errors["password"] = "Password is not correct!"

    # TODO: display errors to the user
    if errors:
        request.session["csrf"] = generate_csrf()
        return templates.TemplateResponse("login.html", {
            "request": request,
            "csrf": request.session["csrf"],
            "errors": errors
        })

    print("Login OK!")
    request.session["user"] = data.username
    return RedirectResponse(url=request.url_for("home"), status_code=303)


@router.post("/logout")
def logout(request: Request, csrf: Annotated[str, Form()]):
    # if the CSRF token is incorrect -> untrusted request
    if not validate_csrf(request, csrf):
        return RedirectResponse(url=request.url_for("home"), status_code=303)
    # if it is correct -> we clear everything
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
