import dotenv
dotenv.load_dotenv(override=True) # .env file 로드

from customRequest import league_v4, getSummoner
from mongo import mongoClient

db=mongoClient.LEAGUEDATA

summoners=[]

summoners.extend(league_v4("challengerleagues"))
summoners.extend(league_v4("grandmasterleagues"))
summoners.extend(league_v4("masterleagues"))

# 추후 로깅 적용
print('--------- 마스터 이상 소환사 정보 insert ---------')

# 임시 request 횟수 count 변수
request_count = 0 
# 추후 예외 처리
for summoner in summoners:
  request_count+=1
  summonerId = summoner["summonerId"]
  filter = {'summonerId':summonerId}
  
  # 추후 예외처리로 삭제
  if not summonerId:
    continue
  
  db.league_entries.update_one(filter, {"$set":summoner}, True) # Upsert:True
  db.summoners.update_one(filter, {"$set":getSummoner(summonerId)}, True) #Upsert:True

