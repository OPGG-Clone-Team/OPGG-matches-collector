# TODO
- python module 추후 가상 환경이나 별도의 패키지 매니저로 분리시키기
- dockerize

# Docker commands
- 컨테이너 삭제  : docker rm [option] [container]
  + [ -f ] : 강제 종료 후 삭제(SIGKILL 시그널 전달)
- 중지된 모든 컨테이너 삭제 : docker container prune
- docker compose 실행 : docker-compose up [option]
  + [ -d ] : 백그라운드 실행
  + [ --build ] : 빌드 후 실행
  + [ -f ] : 컴파일 옵션, -f 뒤에 docker-compose 파일명을 적기
- docker compose로 실행시킨 컨테이너 down : docker-compose down [option]
  + [ --rmi all ] : 사용했던 모든 이미지를 삭제 (관련된 이미지 전부다 삭제됨)
  + [ --rmi local ] : 커스텀 태그가 없는 이미지만 삭제
  + [ -v, --volumes ] : Compose 정의 파일의 데이터 볼륨을 삭제
- 마운트된 볼륨 모두 삭제 : docker volume prune

# Commit convention
- feat : 새로운 기능 추가
- fix : 버그 수정
- docs : 문서 수정
- style : 코드 포맷팅, 세미콜론 누락, 코드 변경이 없는 경우
- refactor : 코드 리펙토링
- test : 테스트 코드, 리펙토링 테스트 코드 추가
- chore : 빌드 업무 수정, 패키지 매니저 수정

# Git README markdown 작성 요령
- 제목, 부제목 입력
  # 가장 큰 크기의 텍스트 (H1)
  ## 그 다음 작은 크기의 텍스트 (H2)
  ### 그 다음 작은 크기의 텍스트 (H3)
  #### 그 다음 작은 크기의 텍스트 (H4)
  ##### 그 다음 작은 크기의 텍스트 (H5)
  ###### 그 다음 작은 크기의 텍스트 (H6)

- 코드 블록 (예시))
  ```python
  result = requests.get(url, headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}).json()
  result_timeline = requests.get(url+'/timeline', headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}).json()
  ```

- 기운 글씨, 굵은 글씨, 취소선
  + _기운 글씨_
  + **굵은 글씨**
  + ~~취소선~~

- 인용글
  > 인용글 1
  > > 인용글 2
  > > > 인용글 3

- 글머리 기호
  + 목록1
    + 목록 1-1
      + 목록 1-1-1

- 구분선, 수평선
  ___
  ***
  ___

- 이미지 삽입
![OPGG 아이콘](data:image/png;base64,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)