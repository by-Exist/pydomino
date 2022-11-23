# Repository

## 의미

Repository 패턴은 2004년 도메인 주도 설계에서 처음으로 등장한 개념입니다.

## 가정

User를 다루는 어떤 상상 속의 서비스가 있다고 가정해봅시다. 서버의 메모리가 무한하고, 서버가 비정상적으로 종료될 가능성이 없다면 서비스는 다음처럼 설계될 수 있을 것입니다.

```python
from dataclasses import dataclass

UserName = str


@dataclass
class User:
    username: str
    password: str


users: dict[UserName, User] = {}


def get(username: str) -> User | None:
    return users.get(username, None)


def edit_password(username: str, new_password: str) -> None:
    user = users.get(username, None)
    assert user
    user.password = new_password


def post(username: str, password: str):
    assert username not in users
    user = User(username, password)
    users[user.username] = user
```

위의 코드 예제를 살펴보면 파이썬의 기본 자료형인 Dictionary를 통해 User 정보를 저장하고 관리하고 있습니다. 그러나 현실적으로는 불가능한 사례입니다. 우리는 Database 또는 File 형태로 영속화하여 정보가 손실되는 일을 방지해야 합니다. Repository 패턴은 저수준과 고수준 사이에 객체를 영속화 할 때 활용할 컬렉션 형태의 인터페이스를 둠으로써 시작됩니다.

위의 예제에 Repository 패턴을 도입한다면 다음과 같이 설계할 수 있습니다.

```python
from dataclasses import dataclass
from typing import Protocol

UserName = str


@dataclass
class User:
    username: str
    password: str


class UserRepository(Protocol):
    def get(self, username: UserName) -> User | None:
        ...

    def add(self, user: User) -> None:
        ...

    def delete(self, user: User) -> None:
        ...


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[UserName, User] = {}

    def get(self, username: UserName) -> User | None:
        return self._users.get(username, None)

    def add(self, user: User) -> None:
        assert user.username not in self._users
        self._users[user.username] = user

    def delete(self, user: User) -> None:
        del self._users[user.username]


users = InMemoryUserRepository()


def get(username: str) -> User | None:
    return users.get(username)


def edit_password(username: str, new_password: str) -> None:
    user = users.get(username)
    assert user
    user.password = new_password


def post(username: str, password: str):
    user = User(username, password)
    users.add(user)
```

## 필요성

레포지토리 패턴의 도입 여부에 따른 장단점을 비교해봅시다.

### 사용한다면

1. 저수준에 대한 세부사항은 숨겨집니다. 어떤 영속화 방식을 선택하든 상관없이 저수준은 인터페이스를 만족하도록 구현될 것이기 때문입니다.
2. 개발 도중 객체를 표현함에 있어 관계형보다 그래프형 DB가 더 올바른 선택이었다는 점을 깨달았다고 생각해 봅시다. 저수준에 의존적인 코드였다면 대규모의 코드 변경이 발생할 것입니다. 그러나 Repository를 사용했다면 Repository 인터페이스를 만족하도록 구현하는 것으로 대처할 수 있습니다.
3. 순수한 도메인 객체를 유지할 수 있습니다. 도메인 객체를 설계할 때 ORM에서 동작하는 Base 클래스를 상속받아야 하는 등의 제약사항이 없습니다.
4. 메모리를 사용하는 테스트용 레포지토리를 정의하고 활용함으로써 저수준에 의존하지 않고도 테스트 로직을 수행할 수 있습니다.

### 사용하지 않는다면

1. 영속화 방식은 이미 대부분 Repository와 유사한 인터페이스를 보유하고 있습니다. 굳이 Repository를 도입하여 복잡도를 높이고 싶지 않습니다.
2. 영속화 방식은 서비스 계획 단계부터 신중하게 선택될 것이며, 변경될 가능성은 없다고 생각해도 무방할 정도로 낮습니다.

결국, 상황에 따라 다른 선택이 필요합니다. 앞으로 진행될 예제에서는 Repository 패턴을 활용하도록 하겠습니다.
