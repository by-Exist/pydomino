# Event Stoming

Event Stoming은 여러 관계자들이 모여 복잡한 비즈니스 도메인을 탐색하는 워크숍 형태로 진행됩니다.

예제 요구사항을 바탕으로 서비스를 설계하고, 각 서비스들이 협업하는 과정을 살펴봅니다.

## 예제 요구사항

1. 사용자가 파일을 업로드합니다.
2. 파일이 업로드 될 때 마다 파일의 이름을 활용해 파일의 위치를 인덱싱합니다.
3. 업로드 된 파일이 영상일 경우, 해당 파일을 스트리밍 처리합니다. 스트리밍 처리된 비디오 파일은 url이 추가됩니다.
4. 대쉬보드에는 업로드 한 파일의 상태(파일 크기, 파일명, 인덱스 여부, 비디오 업로드 여부, 비디오 url, ...) 정보를 제공합니다.

## 구성요소

- Command (Blue): 외부에서 직접적으로 요청되는 요소입니다.
- Event (Orange): 어떠한 일이 수행/발생하였음을 알리는 요소입니다.
- Policy (Purple): 시스템 내부에서 요청되는 요소입니다.
- Aggregate (Yellow): 시스템에서 관리해야 하는 도메인 객체의 이름입니다.
- ReadModel (Green): 읽기 전용 모델입니다.
- Bounded Context (Black line): 서비스를 나누는 단위입니다.
- Pub/Sub Line (Black Arrow): A가 B를 트리거한다는 의미로 사용됩니다.

## 설계

위의 요구사항을 토대로 event stoming을 수행한 결과물은 다음과 같습니다.

![event storming board](../_assets/event_stoming_board.png)

!!! check "Domino!"
    PyDomino는 이벤트 스토밍의 결과물이 도미노 구조와 유사하다는 점에 착안하여 시작되었습니다!

## 설명

이벤트 스토밍 과정을 통해 4개의 마이크로 서비스가 도출되었습니다.

- Drive: 사용자의 파일 업로드를 처리하고 관리하는 서비스입니다.
- VideoProcess: 업로드된 영상 파일을 스트리밍화하는 서비스입니다.
- Indexer: 파일 위치 및 검색을 돕는 서비스입니다.
- Dashboard: 여러 서비스에 파편화된 정보를 한 곳에 모아 확인할 수 있도록 돕는 서비스입니다.

## 앞으로

각각의 서비스를 구현하기 전에, Repository Pattern이란 무엇인지, Message를 전달하기 위해서는 무엇이 필요한지, 각 프로젝트에서 공통적으로 사용될 기본 템플릿은 어떻게 구성되는지 살펴본 후 구현을 시작하겠습니다.
