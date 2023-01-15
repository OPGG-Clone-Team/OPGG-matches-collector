import dotenv
dotenv.load_dotenv(override=True) # .env file 로드

from customRequest import league_exp_v4
from mongo import mongoClient

db=mongoClient.LEAGUEDATA

summoners=[]

summoners.extend(league_exp_v4("CHALLENGER", summoners))
summoners.extend(league_exp_v4("GRANDMASTER", summoners))
summoners.extend(league_exp_v4("MASTER", summoners))

# 추후 로깅 적용
print('--------- 마스터 이상 리그 id insert ---------')

# 추후 예외 처리
for summoner in summoners:
  db.league_entries.update_one({'summonerId':summoner["summonerId"]}, {"$set":summoner}, True)




