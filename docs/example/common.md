# Common

여러 msa 서비스에서 활용될 공통 모듈 common을 정의합니다.

예를 들어 메세지 시스템 클라이언트, 이메일 전송, 파일 저장 등의 유틸성 모듈을 정의하여 공유하며 활용할 수 있습니다.

## Directory Structure

디렉토리 구조에 대해 간략히 설명드리고 진행하겠습니다. common에 포함될 주요 모듈은 message입니다.

\_\_init__.py 파일은 가독성을 위해 제외하였습니다.

```txt
common
  message
    message.py
    ports
      producer.py
      consumer.py
    adapters
      producer
        aiokafka_.py
      consumer
        aiokafka_.py
```

## common.message.message.py

message 객체는 id, type, key, value 속성을 보유합니다.

- id: 메세지의 고유 id입니다. 전역적으로 고유하도록 UUID를 활용합니다. 해당 값은 메세지의 중복 처리를 방지하는데에 활용됩니다.
- type: 메세지의 type입니다. topic을 대분류, type을 소분류로 생각할 수 있습니다.
- key: 메세지의 순서 보장을 위해 사용되는 값입니다. 주로 도메인 객체의 id 값의 문자열 표현이 사용됩니다.
- value: 메세지의 body입니다.

```python
from uuid import UUID


class Message:

    __slots__ = ("id", "type", "key", "value")

    def __init__(self, id: UUID, type: str, key: str, value: str):
        self.id = id
        self.type = type
        self.key = key
        self.value = value
```

## common.message.ports.producer.py

MessageProducer, Serializable 프로토콜을 정의합니다.

```python
from typing import Protocol

from ..message import Message


class Serializable(Protocol):
    def to_message(self) -> Message:
        ...


class MessageProducer(Protocol):
    async def send(self, message: Message) -> None:
        ...
```

## common.message.ports.consumer.py

MessageConsumer, Deserializable 프로토콜을 정의합니다.

```python
from typing import Protocol

from typing_extensions import Self

from ..message import Message


class Deserializable(Protocol):
    @classmethod
    def from_message(cls, message: Message) -> Self:
        ...


class MessageConsumer:
    def subscribe(self, topic: str):
        ...

    async def receive(self) -> Message:
        ...

    async def receive_many(self, timeout_ms: int) -> list[Message]:
        ...

    async def acknowledge(self) -> None:
        ...
```

## common.message.adapter.producer.aiokafka_.py

[aiokafka](https://aiokafka.readthedocs.io/en/stable/)는 Apache Kafka 시스템을 python의 비동기 문법으로 활용할 수 있도록 구성된 오픈소스 라이브러리입니다.

aiokafka를 활용하여 MessageProducer 프로토콜을 만족하는 AIOKafkaMessageProducer를 구현합니다.

```python
from typing import Callable, Iterable

from aiokafka import AIOKafkaProducer as _AIOKafkaProducer  # type: ignore

from ...ports import MessageProducer
from ...message import Message


_str_to_bytes: Callable[[str], bytes] = lambda s: s.encode("utf-8")


class AIOKafkaMessageProducer(MessageProducer):
    def __init__(self, topic: str, bootstrap_servers: str | Iterable[str]):
        self._topic = topic
        self._producer = _AIOKafkaProducer(
            **dict(
                bootstrap_servers=bootstrap_servers
                if isinstance(bootstrap_servers, str)
                else ", ".join(bootstrap_servers),
                key_serializer=_str_to_bytes,
                value_serializer=_str_to_bytes,
            )
        )

    async def start(self):
        await self._producer.start()

    async def stop(self):
        await self._producer.stop()

    async def send(self, message: Message) -> None:
        await self._producer.send_and_wait(  # type: ignore
            topic=self._topic,
            headers=[
                ("id", message.id.hex.encode("utf-8")),
                ("type", message.type.encode("utf-8")),
            ],
            key=message.key,
            value=message.value,
        )
```

## common.message.adapter.consumer.aiokafka_.py

aiokafka를 활용하여 MessageConsumer 프로토콜을 만족하는 AIOKafkaMessageConsumer를 구현합니다.

```python
from typing import Any, Iterable, Protocol, Sequence
from uuid import UUID

from aiokafka import AIOKafkaConsumer as _AIOKafkaConsumer  # type: ignore

from ...message import Message
from ...ports import MessageConsumer


def _bytes_to_str(b: bytes) -> str:
    return b.decode("utf-8")


class ConsumerRecord(Protocol):
    # https://aiokafka.readthedocs.io/en/stable/api.html#aiokafka.structs.ConsumerRecord
    topic: str
    headers: Sequence[tuple[str, bytes]]
    key: str
    value: str


class AIOKafkaMessageConsumer(MessageConsumer):
    def __init__(
        self,
        bootstrap_servers: str | Iterable[str],
        group_id: str,
    ):
        self._topics: set[str] = set()
        self._consumer = _AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=bootstrap_servers
            if isinstance(bootstrap_servers, str)
            else ", ".join(bootstrap_servers),
            group_id=group_id,
            key_deserializer=_bytes_to_str,
            value_deserializer=_bytes_to_str,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            retry_backoff_ms=500,
        )

    async def start(self):
        await self._consumer.start()

    async def stop(self):
        await self._consumer.stop()

    def subscribe(self, *topic: str):
        self._topics.update(topic)

    def _try_convert_to_message(self, record: ConsumerRecord) -> Message | None:
        header = {k: v.decode("utf-8") for k, v in record.headers}
        msg_id, msg_type = header.get("id", ""), header.get("type", "")
        if not msg_id or not msg_type:
            return
        msg = Message(UUID(msg_id), msg_type, record.key, record.value)
        return msg

    async def receive(self) -> Message:
        while True:
            record: ConsumerRecord = await self._consumer.getone()  # type: ignore
            msg = self._try_convert_to_message(record)
            if not msg:
                continue
            return msg

    async def receive_many(self, timeout_ms: int) -> list[Message]:
        data: dict[Any, list[ConsumerRecord]] = await self._consumer.getmany(timeout_ms=timeout_ms)  # type: ignore
        results: list[Message] = []
        for records in data.values():
            for record in records:
                msg = self._try_convert_to_message(record)
                if not msg:
                    continue
                results.append(msg)
        return results

    async def acknowledge(self) -> None:
        await self._consumer.commit()  # type: ignore
```
