from dataclasses import dataclass, field
from types import FunctionType
from typing import Any
from uuid import UUID, uuid4

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
        return dataclass(frozen=True, kw_only=True)(cls)  # type: ignore


class Block(metaclass=BlockMeta):

    _id: UUID = field(default_factory=uuid4)

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "fall_down") or not isinstance(
            getattr(cls, "fall_down"), FunctionType
        ):
            raise NotImplementedError(f"{cls.__name__}에 fall_down 메서드가 정의되어 있지 않습니다.")
