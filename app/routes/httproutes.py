# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse

# for our HTTP routing
from app.auth.session import get_current_user, is_authenticated
from app.auth.crypt import generate_csrf
router = APIRouter()

templates = Jinja2Templates(directory="templates")

# HTML endpoint


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url=request.url_for("login"))

    # logic if logged in
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "FastAPI Game",
        "stats": request.app.state.rMgr
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
        "csrf": request.session["csrf"]
    })


@router.post("/login", response_class=HTMLResponse)
async def loginForm(
    request: Request
):
    return RedirectResponse(url=request.url_for("home"))


@router.get("/dashboard")
async def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url=request.url_for("login"))
    return {"user": request.session["user"]}

# to allow anyone to see the icon, not that important


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
