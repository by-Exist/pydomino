# PyDomino

PyDomino는 이벤트 스토밍의 구조에서 영감을 얻었습니다. 서비스 로직을 블럭 단위로 구조화합니다.

**문서**: [https://by-exist.github.io/pydomino](https://by-exist.github.io/pydomino)

**소스코드**: [https://github.com/by-Exist/pydomino](https://github.com/by-Exist/pydomino)

## 설치

pip를 통해 설치할 수 있습니다.

```command
$ pip install pydomino
```


## 예제

test.py에 아래의 코드를 작성합니다.

```python
from typing import Protocol
from pydomino import Domino, Block, touch
import asyncio


# Port and Adapter
class IEmailSender(Protocol):
    def send(self, __to: str, __body: str):
        ...


class FakeEmailSender(IEmailSender):
    def send(self, __to: str, __body: str):
        print(f"Email sended. (to: {__to}, body: {__body})")


# Blocks
class CreateUser(Block):
    email: str
    password: str


class UserCreated(Block):
    email: str


class SendMail(Block):
    to: str
    body: str


# Application Service
async def create_user(block: CreateUser):
    # create user...
    touch(UserCreated(email=block.email))


async def user_created(block: UserCreated):
    # update user view...
    touch(SendMail(to=block.email, body="Thank you for joining us."))


def send_email(block: SendMail, email_sender: IEmailSender):  # Depend on Port
    email_sender.send(block.to, block.body)


# Domino
domino = Domino()
domino.place(CreateUser, create_user)
domino.place(UserCreated, user_created)
domino.place(SendMail, send_email, email_sender=FakeEmailSender())  # Inject Adapter


async def main():
    block = CreateUser(email="some_user@example.com", password="password")
    await domino.start(block)  # CreateUser -> UserCreated -> SendMail


asyncio.run(main())
```

커맨드를 입력하여 test.py를 실행합니다.

```command
$ python test.py
Email sended. (to: some_user@example.com, body: Thank you for joining us.)
```