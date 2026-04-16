# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Otto Crawford

from fastapi import FastAPI
from app.routes import routes

# actual server 
import uvicorn
from app.lifecycle import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(routes.router)

if __name__ == "__main__":
	uvicorn.run(
		app,
		host="127.0.0.1",
		port=8000,
	)