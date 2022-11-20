from typing import Any, Protocol
from typing_extensions import Self

from ...block import Falldownable


class MessageConsumer(Protocol):
    def __aiter__(self) -> Self:
        ...

    async def __anext__(self) -> Falldownable[Any, Any]:
        ...
