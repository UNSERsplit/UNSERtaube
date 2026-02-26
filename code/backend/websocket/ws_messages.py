from pydantic import BaseModel, TypeAdapter, Field
from typing import Literal, Union, Annotated, Any
from dronemaster import State

class ServerBoundMessage(BaseModel):
    pass

class ClientBoundMessage(BaseModel):
    type: str

### SERVERBOUND START ###
class ConnectToDrone(ServerBoundMessage):
    type: Literal["select_drone"]
    ip: str # TODO replace with drone id
    rtc_sdp: str
    rtc_type: str

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
class StateMessage(ClientBoundMessage):
    type: str = "state"
    state: State

class DroneConnected(ClientBoundMessage):
    type: str = "drone_connected"
    rtc_sdp: str
    rtc_type: str

class DroneDisconnected(ClientBoundMessage):
    type: str = "drone_disconnected"
    reason: str

class Accepted(ClientBoundMessage):
    type: str = "accepted"

class SendWaypoints(ClientBoundMessage):
    type: str = "waypoints"
    context: list[tuple[int,int,int]]

class Error(ClientBoundMessage):
    type: str = "error"
    context: list
    traceback: str
### CLIENTBOUND END ###

messages = Annotated[Union[
    *ServerBoundMessage.__subclasses__()
], Field(discriminator="type")]

IncommingMessage: TypeAdapter[messages] = TypeAdapter(messages)