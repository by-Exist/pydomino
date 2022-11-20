from contextvars import ContextVar, Token
from types import TracebackType
from typing import Any, ContextManager

from typing_extensions import Self

from .block import Falldownable

Block = Falldownable
AnyBlock = Block[Any, Any]

_touched_blocks_context_var: ContextVar[set[AnyBlock]] = ContextVar("touched_blocks")


class TouchContextError(LookupError):
    ...


class TouchContext(ContextManager["TouchContext"]):

    _token: Token[set[AnyBlock]]
    touched_blocks: set[AnyBlock]

    def __enter__(self) -> Self:
        self._token = _touched_blocks_context_var.set(set())
        return self

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        self.touched_blocks = _touched_blocks_context_var.get()
        _touched_blocks_context_var.reset(self._token)


def touch(*blocks: AnyBlock):
    try:
        _touched_blocks_context_var.get().update(blocks)
    except LookupError:
        raise RuntimeError("touch 함수는 반드시 TouchContext 내에서 실행되어야 합니다.")
