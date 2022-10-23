# Action Function

## Action Function은

* 도미노에 배치된 어떠한 블럭이 쓰러지는 동작에 비유됩니다.
* Block을 첫 번째 인자, 나머지 종속성을 기타 인자로 제공받는 사용자 정의 함수입니다.

## 정의

Action Function의 첫 번째에 전달될 Block이 필요합니다.

```python
from pydomino import Block


class WriteLog(Block):
    text: str
```

해당 Block을 첫 번째 인자로, 기타 위치 또는 키워드 인자로 종속성을 필요로 하는 Action Function을 정의합니다.

Action Function은 요구사항에 따라 동기 함수 또는 코루틴을 반환하는 비동기 함수로 작성할 수 있습니다.

```python
from typing import Protocol
from pydomino import Block


class WriteLog(Block):
    text: str


class ILogger(Protocol):

    def log(self, __text: str):
        ...


def write_log(block: WriteLog, logger: ILogger):
    logger.log(block.text)


# or,
async def write_log_async(block: WriteLog, logger: ILogger):
    logger.log(block.text)
```

## 사용처

- Domino 객체의 place 메서드에서 Block Class와 매핑할 때 사용합니다.