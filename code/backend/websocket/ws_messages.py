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

class StartNetworkScan(ServerBoundMessage):
    type: Literal["scan_network"]
### SERVERBOUND END ###

### CLIENTBOUND START ###
class NewDroneFound(ClientBoundMessage):
    type: str = "new_drone"
    ip: str

class NetworkScanFinished(ClientBoundMessage):
    type:str  = "scan_finished"
### CLIENTBOUND END ###

messages = Annotated[Union[
    ConnectToDrone,
    StartNetworkScan
], Field(discriminator="type")]

IncommingMessage: TypeAdapter[messages] = TypeAdapter(messages)