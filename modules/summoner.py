# 상위 경로 패키지 로드
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# 추후 환경변수 로드하는 공통로직 분리하기
from config import mongo as mongo
from riot_requests import summoner_v4
from decorator.trycatch_wrapper import trycatch

# LEAGUEDATA db의 summoners만 담당
db = mongo.mongoClient.LEAGUEDATA
col = "summoners"

@trycatch
def update(summonerName):
  # 1. league_entries에서 summonerName 과 일치하는 데이터 조회
  summoner_brief = db.league_entries.find_one({"summonerName":summonerName})
  
  # 1-1. 없다면 raise Exception
  if not summoner_brief:
    raise Exception("league_entries collection에 소환사 정보가 없습니다.")
  
  # 2. summonerId를 가져와서 summoner_v4의 summoner 정보를 가져오기
  summoner = summoner_v4.getSummoner(summoner_brief["summonerId"])
  
  # 2-1. 없다면 raise Exception
  if not summoner:
    raise Exception("소환사 정보를 가져오는 데 실패했습니다.")
  
  # 3. db에 저장
  # upsert=True
  db[col].update_one(
      {"puuid":summoner["puuid"]},
      {"$set":summoner},
      True)
  print(f"소환사 {summonerName}의 정보를 성공적으로 업데이트했습니다.")

if __name__=="__main__":
  update("칼과 창 방패")