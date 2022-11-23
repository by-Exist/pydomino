# PyDomino

PyDomino는 이벤트 스토밍, 헥사고날 아키텍처, 커맨드 디자인 패턴에서 영감을 얻었습니다.

서비스 로직을 블럭 단위로 구조화합니다.

**문서**: [https://by-exist.github.io/pydomino](https://by-exist.github.io/pydomino)

**소스코드**: [https://github.com/by-Exist/pydomino](https://github.com/by-Exist/pydomino)

## 설치

pip를 통해 설치할 수 있습니다. (작업중...)

```console
pip install pydomino
```

## 예제

```python title="test.py"
import asyncio
from typing import Protocol

from pydomino import Block, Domino, touch


# Port
class IEmailSender(Protocol):
    def send(self, __to: str, __body: str):
        ...


# Blocks
class CreateUser(Block):
    email: str
    password: str

    def fall_down(self):
        touch(UserCreated(email=self.email))


class UserCreated(Block):
    email: str

    def fall_down(self):
        touch(SendMail(to=self.email, body="Thank you for joining us."))


class SendMail(Block):
    to: str
    body: str

    def fall_down(self, email_sender: IEmailSender):
        email_sender.send(self.to, self.body)


# Adapter
class FakeEmailSender(IEmailSender):
    def send(self, __to: str, __body: str):
        print(f"Email sended. (to: {__to}, body: {__body})")


# Domino
domino = Domino()
domino.place(CreateUser)
domino.place(UserCreated)
domino.place(SendMail, email_sender=FakeEmailSender())  # Inject Dependency


async def main():
    block = CreateUser(email="some_user@example.com", password="password")

    # CreateUser -> UserCreated -> SendMail
    await domino.start(block)


asyncio.run(main())
```

```command
$ python test.py
Email sended. (to: some_user@example.com, body: Thank you for joining us.)
```
