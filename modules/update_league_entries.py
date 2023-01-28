#########
#해당 모듈은 확장된 Rate Limit을 받기 전까지 임시로 사용할 masterLeague이상의 소환사 전적만 검색하기 때문에,

##########
import dotenv
dotenv.load_dotenv(override=True) # .env file 로드

from riot_requests.riot_requests import league_v4, getSummoner
from mongo import mongoClient

db=mongoClient.LEAGUEDATA

summoners=[]

summoners.extend(league_v4("challengerleagues"))
summoners.extend(league_v4("grandmasterleagues"))
summoners.extend(league_v4("masterleagues"))

# 추후 로깅 적용
print('--------- 마스터 이상 소환사 정보 insert ---------')

#league_entries와 각각의 소환사 정보 업데이트

print(f"총 소환사 수 : {len(summoners)}")

# 무조건 한번 조회 시에 갱신해줘야 함 (정적인 데이터 X)
for summoner in summoners:
  summonerId = summoner["summonerId"]
  filter = {'summonerId':summonerId}
  
  # 추후 예외처리로 삭제
  if not summonerId:
    continue
  
  db.league_entries.update_one(filter, {"$set":summoner}, True) # Upsert:True
  db.summoners.update_one(filter, {"$set":getSummoner(summonerId)}, True) # Upsert:True

