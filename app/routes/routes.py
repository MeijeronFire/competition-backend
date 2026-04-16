from fastapi import APIRouter, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.client import initClient, delClient
from app.models.verify import RegisterPacket
from pydantic import ValidationError

router = APIRouter()

templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")


## HTML endpoint
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "FastAPI Game"
    })

# TRANSPORT LAYER
@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    # after this point, never access the websocket object directly
    connectedUser = await initClient(ws)
    ws.app.state.mgr.connect(connectedUser)
    # interpret the first packet, which contains
    # client-defined information
    msg = await connectedUser.ws.receive_json()

    try:
        regPacket = RegisterPacket.model_validate(msg)
    except ValidationError:
        print(f"client {connectedUser} set an incorrect JSON registration packet.")
        # TODO: make this more verbose to explain which packet would be expected
        await ws.send_json({
            "type": "error",
            "errorType": "Incorrect JSON registration packet sent"
        })
        await ws.close()
        return
    
    # now we know we have a correct JSON packet so we can start interpreting the connection
    connectedUser.uname(regPacket.name)
    # add this client to the list of players
    ws.app.state.game.addPlayer(connectedUser.uuid, regPacket.name)
    # MAKE THIS CONDITIONAL
    # which function to execute when the user receives a packet

    # we send a response to the user
    await ws.send_json({
        "type": "regResp",
        "msg": "Registration OK."
    })

    # do this until the websocket disconnects unexpectedly
    try: 
        while 1:
            data = await ws.receive_json()
            print(f"We got data: {data}")
            await ws.app.state.msgQueue.put((connectedUser, data))
    except WebSocketDisconnect:
        # on disconnect run the manager disconnect hook
        await delClient(connectedUser)
        # delete it from known connections
        ws.app.state.mgr.disconnect(ws)
        return
