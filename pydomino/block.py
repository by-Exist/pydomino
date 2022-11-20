from typing import Any, Coroutine, ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class Block(Protocol):
    fall_down: Any


class Falldownable(Protocol[P, R_co]):
    def fall_down(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> R_co | Coroutine[Any, Any, R_co]:
        ...
