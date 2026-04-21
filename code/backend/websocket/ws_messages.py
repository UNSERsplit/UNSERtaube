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
    name: str
    ip: str

class DisconnectFromDrone(ServerBoundMessage):
    type: Literal["disconnect"]

class TakeOff(ServerBoundMessage):
    type: Literal["takeoff"]

class StartRecording(ServerBoundMessage):
    type: Literal["record_start"]

class StopRecording(ServerBoundMessage):
    type: Literal["record_stop"]
    route_name: str

class ReplayRoute(ServerBoundMessage):
    type: Literal["replay_recording"]
    id: str

class Emergency(ServerBoundMessage):
    type: Literal["emergency"]

class Land(ServerBoundMessage):
    type: Literal["land"]

class DebugSendRawCommand(ServerBoundMessage):
    type: Literal["rawcommand"]
    command: str
    wait_for_response: bool
    timeout: int

class DebugFineTuneVision(ServerBoundMessage):
    type: Literal["finetune_vision"]
    show_processed_output: bool
    hue_lower: int
    hue_upper: int
    saturation_lower: int
    saturation_upper: int
    value_lower: int
    value_upper: int

class ServerBoundKeepAlive(ServerBoundMessage):
    type: Literal["keepalive"]

class FunkiMessage(ServerBoundMessage):
    type: Literal["rc"]
    yaw: float
    pitch: float
    roll: float
    throttle: float

class SetStartupMatrix(ServerBoundMessage):
    type: Literal["set_init_matrix"]
    data: str

class SetMatrix(ServerBoundMessage):
    type: Literal["set_matrix"]
    data: str

class SetStaticLed(ServerBoundMessage):
    type: Literal["static_led"]
    red: int
    green: int
    blue: int

class SetPulsingLed(ServerBoundMessage):
    type: Literal["pulsing_led"]
    red: int
    green: int
    blue: int
    freq: int

class SetFlashingLed(ServerBoundMessage):
    type: Literal["flashing_led"]
    red1: int
    green1: int
    blue1: int
    freq: int
    red2: int
    green2: int
    blue2: int

### SERVERBOUND END ###

### CLIENTBOUND START ###
class ClientBoundKeepAlive(ClientBoundMessage):
    type: str = "keepalive" # TODO

class DebugCommandAnswer(ClientBoundMessage):
    type: str = "rawanswer"
    answer: str

class StateMessage(ClientBoundMessage):
    type: str = "state"
    state: State

class RecordingResult(ClientBoundMessage):
    type: str = "recording_name"
    name: str

class DroneConnected(ClientBoundMessage):
    type: str = "drone_connected"

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
    *ServerBoundMessage.__subclasses__() #type: ignore
], Field(discriminator="type")]

IncommingMessage: TypeAdapter[messages] = TypeAdapter(messages) #type: ignore