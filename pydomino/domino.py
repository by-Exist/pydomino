import asyncio
from typing import (
    Any,
    Callable,
    Coroutine,
    Iterable,
    Literal,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

from .block import Falldownable
from .concurrency import run_in_threadpool
from .context import TouchContext

Block = Falldownable
AnyBlock = Block[Any, Any]


P = ParamSpec("P")
R = TypeVar("R")


class NotPlacedBlock(RuntimeError):
    ...


class Domino:
    def __init__(self) -> None:
        self._deps: dict[type[AnyBlock], tuple[tuple[Any], dict[str, Any]]] = {}

    def place(self, block_type: type[Block[P, Any]], *args: P.args, **kwargs: P.kwargs):
        self._deps[block_type] = (args, kwargs)

    @overload
    async def start(
        self,
        block: Block[Any, R],
        return_effect: Literal[False] = False,
        _direct: bool = True | False,
    ) -> R:
        ...

    @overload
    async def start(
        self,
        block: Block[Any, R],
        return_effect: Literal[True] = True,
        _direct: bool = True | False,
    ) -> tuple[R, asyncio.Future[list[Any]]]:
        ...

    async def start(
        self,
        block: Block[Any, R],
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
        block: Block[P, R],
    ) -> tuple[R, Iterable[AnyBlock]]:
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
        block: AnyBlock,
    ):
        ...

    async def post_fall_down(
        self,
        block: AnyBlock,
        result: Any,
        touched_blocks: Iterable[AnyBlock],
    ):
        ...

    async def exception_fall_down(
        self,
        block: AnyBlock,
        exc: Exception,
    ):
        ...
