# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

import sys
import os
from fastapi import FastAPI
from app.routes import siteroutes, wsroutes, sseroutes, apiroutes
from fastapi.staticfiles import StaticFiles
from typing import cast

# setup loggin
import app.utils

# actual server
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from app.lifecycle import lifespan

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# allows for us to authenticate users
#################################
# DANGEROUS DANGEROUS DANGEROUS #
_SECRET_KEY = "dev-key"
# DANGEROUS DANGEROUS DANGEROUS #
#################################

app.add_middleware(
    SessionMiddleware,
    secret_key=_SECRET_KEY,
    same_site="lax",  # for CSRF
)

# print warning if above is not secure
if _SECRET_KEY in ["dev-key", "test", "foo", "bar", "foobar"]:
    print(
        "\033[1;33mWARNING: \033[0m Insecure session middleware _SECRET_KEY! Change for any serious use!"
    )

# include everything in router/
app.include_router(wsroutes.router)
app.include_router(siteroutes.router)
app.include_router(sseroutes.router)
app.include_router(apiroutes.router)


# Detect if we are running with reload enabled
if "--reload" in sys.argv or os.environ.get("RUN_MAIN") == "true":
    print("\033[1;33mWARNING: \033[0m Running in reload mode! Turn off in prod!")


# for when the server is run with python rather than uvicorn
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
