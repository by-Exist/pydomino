from dataclasses import dataclass
from dataclasses import field as field
from typing import Any

from typing_extensions import Self, dataclass_transform


@dataclass_transform(kw_only_default=True)
class BlockMeta(type):
    def __new__(
        cls: type[Self],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwds: Any,
    ) -> Self:
        cls = super().__new__(cls, name, bases, namespace)
        return dataclass(kw_only=True)(cls)  # type: ignore


class Block(metaclass=BlockMeta):
    ...
