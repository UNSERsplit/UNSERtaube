from pydantic import BaseModel, create_model
from .ws_messages import ServerBoundMessage, ClientBoundMessage


def model_from_parent_class(clazz: type[BaseModel]) -> type[BaseModel]:
    a = {}
    for subclass in clazz.__subclasses__():
        a[subclass.__name__] = subclass, None

    return create_model(clazz.__name__, **a)

MsgServerDef = model_from_parent_class(ServerBoundMessage)
MsgClientDef = model_from_parent_class(ClientBoundMessage)

class MsgDef(BaseModel):
    serverbound: MsgServerDef # type: ignore
    clientbound: MsgClientDef # type: ignore
