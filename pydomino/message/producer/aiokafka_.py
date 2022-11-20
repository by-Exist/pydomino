from typing import Callable, Iterable

from aiokafka import AIOKafkaProducer  # type: ignore

from ..message import Serializer
from .base import MessageProducer as _MessageProducer

_str_to_bytes: Callable[[str], bytes] = lambda s: s.encode("utf-8")


class AIOKafkaMessageProducer(_MessageProducer):
    def __init__(self, topic: str, bootstrap_servers: str | Iterable[str]):
        self._topic = topic
        self._started = False
        self._producer: AIOKafkaProducer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers
            if isinstance(bootstrap_servers, str)
            else ", ".join(bootstrap_servers),
            key_serializer=_str_to_bytes,
            value_serializer=_str_to_bytes,
        )

    async def produce(self, serializable: Serializer) -> None:
        if not self._started:
            await self._producer.start()
            self._started = True
        message = serializable.to_message()
        await self._producer.send_and_wait(  # type: ignore
            topic=self._topic,
            headers=[("type", bytes(type(serializable).__name__, encoding="utf-8"))],
            timestamp_ms=message.timestamp_ms,
            key=message.key,
            value=message.value,
        )
