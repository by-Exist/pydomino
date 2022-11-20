from typing import Any, Iterable, Protocol, Sequence

from aiokafka import AIOKafkaConsumer as _AIOKafkaConsumer  # type: ignore

from ...block import Falldownable
from ..message import Deserializer, Message
from .base import MessageConsumer as MessageConsumer


class MessageRecord(Protocol):
    topic: str
    timestamp: int
    key: str
    value: str
    headers: Sequence[tuple[str, bytes]]


def _bytes_to_str(b: bytes) -> str:
    return b.decode("utf-8")


class DeserializableBlock(Falldownable[Any, Any], Deserializer, Protocol):
    ...


class AIOKafkaMessageConsumer(MessageConsumer):

    _consumer: _AIOKafkaConsumer

    def __init__(
        self,
        bootstrap_servers: str | Iterable[str],
        group_id: str,
    ):
        self._topic_block_map: dict[str, dict[str, type[DeserializableBlock]]] = {}
        self._config = {
            "bootstrap_servers": bootstrap_servers
            if isinstance(bootstrap_servers, str)
            else ", ".join(bootstrap_servers),
            "group_id": group_id,
            "key_deserializer": _bytes_to_str,
            "value_deserializer": _bytes_to_str,
            "enable_auto_commit": False,
            "auto_offset_reset": "earliest",
            "retry_backoff_ms": 500,
        }

    def watch(self, topic: str, block_type: type[DeserializableBlock]):
        self._topic_block_map.setdefault(topic, {})[block_type.__name__] = block_type

    async def start(self):
        self._consumer = _AIOKafkaConsumer(
            *self._topic_block_map.keys(),
            **self._config,
        )
        await self._consumer.start()

    async def stop(self):
        await self._consumer.stop()

    async def commit(self):
        await self._consumer.commit()  # type: ignore

    def __aiter__(self):
        return self

    async def __anext__(self) -> DeserializableBlock:
        while True:
            record: MessageRecord = await self._consumer.__anext__()
            record_headers = {
                k: v.decode(encoding="utf-8") for (k, v) in record.headers
            }
            block_type_name = record_headers.get("type", None)
            if not block_type_name:
                continue
            block_type = self._topic_block_map[record.topic].get(block_type_name, None)
            if not block_type:
                continue
            message = Message(
                key=record.key, value=record.value, timestamp=record.timestamp
            )
            return block_type.from_message(message)
