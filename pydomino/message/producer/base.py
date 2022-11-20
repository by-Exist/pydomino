from typing import Protocol
from ..message import Serializer


class MessageProducer(Protocol):
    async def produce(self, serializable: Serializer) -> None:
        ...
