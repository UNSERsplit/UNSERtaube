from pydantic import BaseModel, TypeAdapter, Field
from typing import Literal, Union, Annotated

class ServerBoundMessage(BaseModel):
    pass

class ClientBoundMessage(BaseModel):
    type: str

### SERVERBOUND START ###
class ConnectToDrone(ServerBoundMessage):
    type: Literal["select_drone"]
    ip: str # TODO replace with drone id

class TakeOff(ServerBoundMessage):
    type: Literal["takeoff"]

class Land(ServerBoundMessage):
    type: Literal["land"]

class FunkiMessage(ServerBoundMessage):
    type: Literal["rc"]
    yaw: float
    pitch: float
    roll: float
    throttle: float
### SERVERBOUND END ###

### CLIENTBOUND START ###
class NewDroneFound(ClientBoundMessage):
    type: str = "new_drone"
    ip: str

class NetworkScanFinished(ClientBoundMessage):
    type: str  = "scan_finished"

class DroneConnected(ClientBoundMessage):
    type: str = "drone_connected"

class DroneDisconnected(ClientBoundMessage):
    type: str = "drone_disconnected"
### CLIENTBOUND END ###

messages = Annotated[Union[
    ConnectToDrone,
    TakeOff,
    Land,
    FunkiMessage
], Field(discriminator="type")]

IncommingMessage: TypeAdapter[messages] = TypeAdapter(messages)