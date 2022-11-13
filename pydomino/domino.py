import asyncio
from contextvars import ContextVar, Token
from types import TracebackType
from typing import (
    Any,
    Callable,
    ContextManager,
    Coroutine,
    Iterable,
    Literal,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import Self

from .block import Block
from .concurrency import run_in_threadpool

#
# Block Protocol
#
P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class IBlock(Protocol[R_co, P]):
    def fall_down(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> R_co | Coroutine[Any, Any, R_co]:
        ...


IAnyBlock = IBlock[Any, Any]


#
# Touch Context
#
_touched_blocks_context_var: ContextVar[set[IAnyBlock]] = ContextVar("touched_blocks")


class TouchContextError(LookupError):
    ...


class TouchContext(ContextManager["TouchContext"]):

    _token: Token[set[IAnyBlock]]
    touched_blocks: set[IAnyBlock]

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


def touch(*blocks: IAnyBlock):
    try:
        _touched_blocks_context_var.get().update(blocks)
    except LookupError:
        raise RuntimeError("touch 함수는 반드시 TouchContext 내에서 실행되어야 합니다.")


#
# Domino
#
R = TypeVar("R")


class NotPlacedBlock(RuntimeError):
    ...


class Domino:
    def __init__(self) -> None:
        self._deps: dict[type[IAnyBlock], tuple[tuple[Any], dict[str, Any]]] = {}

    def place(
        self, block_type: type[IBlock[Any, P]], *args: P.args, **kwargs: P.kwargs
    ):
        self._deps[block_type] = (args, kwargs)

    @overload
    async def start(
        self,
        block: IBlock[R, Any],
        return_effect: Literal[False] = False,
        _direct: bool = True | False,
    ) -> R:
        ...

    @overload
    async def start(
        self,
        block: IBlock[R, Any],
        return_effect: Literal[True] = True,
        _direct: bool = True | False,
    ) -> tuple[R, asyncio.Future[list[Any]]]:
        ...

    async def start(
        self,
        block: IBlock[R, Any],
        return_effect: bool = False,
        _direct: bool = True,
    ) -> R | tuple[R, asyncio.Future[list[Any]]]:
        await self.pre_fall_down(block)
        try:
            result, touched_blocks = await asyncio.create_task(self._fall_down(block))
        except Exception as e:
            await self.exception_fall_down(block, e)
            if _direct:
                raise e
            return  # type: ignore
        await self.post_fall_down(block, result, touched_blocks)
        effect = asyncio.gather(
            *(self.start(block, _direct=False) for block in touched_blocks)
        )
        if return_effect:
            return result, effect
        await effect
        return result

    async def _fall_down(
        self,
        block: IBlock[R, P],
    ) -> tuple[R, Iterable[IAnyBlock]]:
        fall_down: Callable[..., R | Coroutine[Any, Any, R]] = getattr(
            block, "fall_down"
        )
        try:
            args, kwargs = self._deps[type(block)]
        except KeyError:
            raise NotPlacedBlock(
                f"place되지 않은 Block은 사용할 수 없습니다. ({type(block).__name__})"
            )
        with TouchContext() as catcher:
            if asyncio.iscoroutinefunction(fall_down):
                fall_down = cast(Callable[..., Coroutine[Any, Any, R]], fall_down)
                result = await fall_down(*args, **kwargs)
            else:
                fall_down = cast(Callable[..., R], fall_down)
                result = await run_in_threadpool(fall_down, *args, **kwargs)
        return result, catcher.touched_blocks

    async def pre_fall_down(
        self,
        block: IBlock[Any, Any],
    ):
        ...

    async def post_fall_down(
        self,
        block: IBlock[Any, Any],
        result: Any,
        touched_blocks: Iterable[IBlock[Any, Any]],
    ):
        ...

    async def exception_fall_down(
        self,
        block: IBlock[Any, Any],
        exc: Exception,
    ):
        ...
