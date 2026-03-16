from pydantic import BaseModel, ConfigDict

class BaseMessage(BaseModel):
    action: str
    model_config = ConfigDict(extra="allow")

class RegisterPacket(BaseMessage):
    name: str
    room: str