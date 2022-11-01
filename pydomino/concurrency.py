from functools import partial
from typing import Callable, ParamSpec, TypeVar

import anyio

P = ParamSpec("P")
R = TypeVar("R")


async def run_in_threadpool(
    func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> R:
    if kwargs:
        func = partial(func, **kwargs)  # type: ignore
    return await anyio.to_thread.run_sync(func, *args)
