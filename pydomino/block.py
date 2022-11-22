from typing import Any, Coroutine, ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class RequiredFallDownMethod(RuntimeError):
    ...


class FallDownIsNotMethod(RuntimeError):
    ...


class Block(Protocol):
    fall_down: Any

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "fall_down"):
            raise RequiredFallDownMethod(f"{cls.__name__}에 fall_down 메서드가 정의되어 있지 않습니다.")
        if not callable(getattr(cls, "fall_down", None)):
            raise FallDownIsNotMethod(f"{cls.__name__}에 정의된 fall_down은 메서드여야 합니다.")


class Falldownable(Protocol[P, R_co]):
    def fall_down(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> R_co | Coroutine[Any, Any, R_co]:
        ...
