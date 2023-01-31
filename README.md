mongoDB docker shell 접속 : mongosh -u [root계정] -p [root_password]


collection의 document 수 조회 : db.collection.find({}).count()
# mongoDB 외부접속 허용 코드 작성해야 함
# python module 추후 가상 환경이나 별도의 패키지 매니저로 분리시키기


# docker 

컨테이너 삭제  : docker rm [option] [container]
  [ -f ] : 강제 종료 후 삭제(SIGKILL 시그널 전달)
중지된 모든 컨테이너 삭제 : docker container prune
docker compose 실행 : docker-compose up [option]
  [ -d ] : 백그라운드 실행
docker compose로 실행시킨 컨테이너 down : docker-compose down [option]
  [ --rmi all ] : 사용했던 모든 이미지를 삭제 (관련된 이미지 전부다 삭제됨)
  [ --rmi local ] : 커스텀 태그가 없는 이미지만 삭제
  [ -v, --volumes ] : Compose 정의 파일의 데이터 볼륨을 삭제
