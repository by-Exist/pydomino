from datetime import datetime, timedelta, timezone
from typing import Protocol

from typing_extensions import Self

Key = str
Json = str
UnixEpochTime = int

_epoch_datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _datetime_to_timestamp(datetime: datetime) -> UnixEpochTime:
    return (datetime.replace(tzinfo=timezone.utc) - _epoch_datetime) // timedelta(
        milliseconds=1
    )


class Message:

    __slots__ = ("key", "value", "timestamp_ms")

    key: Key
    value: Json
    timestamp_ms: UnixEpochTime

    def __init__(self, key: Key, value: Json, timestamp: datetime | int):
        self.key = key
        self.value = value
        self.timestamp_ms = (
            timestamp
            if isinstance(timestamp, int)
            else _datetime_to_timestamp(timestamp)
        )


class Serializer(Protocol):
    def to_message(self) -> Message:
        ...


class Deserializer(Protocol):
    @classmethod
    def from_message(cls, message: Message) -> Self:
        ...
