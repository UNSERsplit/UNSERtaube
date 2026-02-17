from pydantic import BaseModel, TypeAdapter, Field
from typing import Literal, Union, Annotated, Any

class ServerBoundMessage(BaseModel):
    pass

class ClientBoundMessage(BaseModel):
    type: str

### SERVERBOUND START ###
class ConnectToDrone(ServerBoundMessage):
    type: Literal["select_drone"]
    ip: str # TODO replace with drone id

class DisconnectFromDrone(ServerBoundMessage):
    type: Literal["disconnect"]

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
    reason: str

class Accepted(ClientBoundMessage):
    type: str = "accepted"

class Error(ClientBoundMessage):
    type: str = "error"
    context: tuple[Any]
### CLIENTBOUND END ###

messages = Annotated[Union[
    *ServerBoundMessage.__subclasses__()
], Field(discriminator="type")]

IncommingMessage: TypeAdapter[messages] = TypeAdapter(messages)