# 상위 경로 패키지 로드
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# 추후 환경변수 로드하는 공통로직 분리하기
from config import mongo as mongo
from riot_requests import match_v4
from decorator.trycatch_wrapper import trycatch

# LEAGUEDATA db의 summoner_matches만 담당
db = mongo.mongoClient.LEAGUEDATA
col = "summoner_matches"

@trycatch
def update(summonerName):
  summoner = db["summoners"].find_one({"name": summonerName})
  
  # TODO : 좀이따가 summoner 타고 들어가게 변경
  if not summoner:
    raise Exception("유저를 찾을 수 없음")

  puuid = summoner["puuid"]

  # 모든 matchId 담을 변수, 최근 matchId 우선 가져오기
  all_match_ids = set(match_v4.getSummonerMatches(puuid))

  old_summoner_matches = db[col].find_one({"puuid": puuid})

  if old_summoner_matches:
    all_match_ids.update(old_summoner_matches["summoner_match_ids"])
    
  # Upsert:True
  # id 역순으로 정렬해야 최신순으로 저장
  db[col].update_one(
      {'puuid':puuid},
      {"$set": {"summoner_match_ids": sorted(
          list(all_match_ids), reverse=True)}},
      True)  
  
  print(f'소환사 {summonerName}님의 matchId list가 업데이트되었습니다.')
    
if __name__=="__main__":
  update("칼과 창 방패")