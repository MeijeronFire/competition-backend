from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

templates = Jinja2Templates(directory="templates")

## HTML endpoint
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("item.html", {
        "request": request,
        "title": "FastAPI Game",
        "stats": request.app.state.rMgr,
    })
    # return "Raaaah"