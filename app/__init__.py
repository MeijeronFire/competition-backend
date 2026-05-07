# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import FastAPI
from app.routes import wsroutes, httproutes
from fastapi.staticfiles import StaticFiles

# actual server
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from app.lifecycle import lifespan

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key="dev-key",  # TODO: change later!
    same_site="lax"  # for CSRF
)

app.include_router(wsroutes.router)
app.include_router(httproutes.router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
