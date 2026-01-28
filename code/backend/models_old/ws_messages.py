from pydantic import BaseModel
from typing import Literal, Union

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
    type = "new_drone"
    ip: str

class NetworkScanFinished(ClientBoundMessage):
    type = "scan_finished"
### CLIENTBOUND END ###

IncommingMessage = Union[
    ConnectToDrone,
    StartNetworkScan
]