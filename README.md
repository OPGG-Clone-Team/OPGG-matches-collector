mongoDB docker shell 접속 : mongosh -u [root계정] -p [root_password]

collection의 document 수 조회 : db.collection.find({}).count()
# mongoDB 외부접속 허용 코드 작성해야 함
# python module 추후 가상 환경이나 별도의 패키지 매니저로 분리시키기
