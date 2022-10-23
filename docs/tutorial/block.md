# Block


## Block은

* 도미노에 배치되는 하나의 블럭으로 비유됩니다.
* Action Function에 제공되는 값 객체입니다.
    * 특정 Callable이 요구하는 인자들을 한 객체로 그룹화합니다.
* 인스턴스는 생성 이후 속성을 변경할 수 없습니다.


## 정의

자신만의 Block을 정의하기 위해서는 Block을 상속해야 합니다.

```python
from uuid import UUID, uuid4
from pydomino import Block, field


class CustomBlock(Block):
    kwarg1: str
    kwarg2: bool | None = None
    kwarg3: UUID = field(default_factory = uuid4)
```


## 인스턴스 생성

Typing 기능을 통해 인스턴스 생성 시 필요한 인자 정보를 제공받을 수 있습니다.

![block typing](../_assets/block_typing.png)


## Frozen

한번 생성된 Block 인스턴스의 속성은 변경 불가능합니다.

```python
b = CustomBlock(kwarg1="foo")

b.kwarg1 = "bar"  # raise FrozenInstanceError
```


## 사용처

* Block Class는
    * Action Function의 타이핑에서 사용합니다.
    * Domino 객체의 place 메서드에서 Action Function과 매핑할 때 사용합니다.
* Block Instance는
    * Domino 객체의 start 메서드에 전달되어 도미노 동작을 시작할 때 사용합니다.
