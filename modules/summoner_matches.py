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
  
  if not summoner:
    raise Exception("유저를 찾을 수 없음")

  puuid = summoner["puuid"]

  # TODO set대신에 가장 최근에 했던 게임정보(matchId) 하나만 저장해두고, 이후 Riot API 요청시 비교만 하도록 변경하기
  
  # 가장 최근 match id 가져오기
  old_matches = db[col].find_one({"puuid":puuid})
  
  # 모든 matchId 담을 변수, 최근 matchId 우선 가져오기 (100개씩))
  all_match_ids = set(match_v4.getSummonerMatches(
      puuid, count = 100))
  
  # 다음 페이지 조회 시 이용하는 변수
  start_index=100
  
  if old_matches:
    latest_match_id = old_matches["summoner_match_ids"][0]
    
    # API로 최근 전적 가져온 후 그 안에 latest_match_id가 존재하면 db와 sync가 맞음
    # 그렇지 않으면 계속 가져와서 all_matches_ids에 갖다붙이기
    while latest_match_id not in all_match_ids:
      all_match_ids.update(match_v4.getSummonerMatches(puuid, start = start_index, count = 100))
      start_index+=100
      
  else:
    while True:
      new_match_list = match_v4.getSummonerMatches(puuid, start = start_index, count = 100)
      if len(new_match_list)!=0:
        all_match_ids.update(new_match_list)
        start_index+=100
      else:
        break
      
  # TODO 정렬 어떻게 할건지는 좀 더 생각해봐야 할듯
  # Upsert:True
  # id 역순으로 정렬해야 최신순으로 저장
  db[col].update_one(
      {'puuid': puuid},
      {"$set": {"summoner_match_ids": sorted(
          list(all_match_ids), reverse=True)}},
      True)

  print(f'소환사 {summonerName}님의 matchId list가 업데이트되었습니다.')
    
if __name__=="__main__":
  update("칼과 창 방패")