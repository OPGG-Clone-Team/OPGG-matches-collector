from riot_requests import match_v4
from error.custom_exception import *

# LEAGUEDATA db의 summoner_matches 담당
col = "summoner_matches"

def update(db, summonerName):
  """
  소환사의 최근 match Id 리스트를 DB에 업데이트

  Args:
      db (mongoClient): mongoDB connection
      summonerName (String): 소환사이름

  Raises:
      Exception: _description_
  
  Returns:
      puuid (str) : 소환사의 puuid
  """
  summoner = db["summoners"].find_one({"name": summonerName})
  
  if not summoner:
    raise DataNotExists("데이터베이스에서 소환사 정보를 찾을 수 없습니다.")

  puuid = summoner["puuid"]
  
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

  return summoner["puuid"]

def findRecentMatchIds(db, puuid, startIdx=0, size=30):
  """
  소환사의 최근 Match Id 리스트를 반환

  Args:
      db (connection): MongoDB connection
      puuid (str): 소환사 puuid
      startIdx (int, optional): 시작할 인덱스 위치. Defaults to 0.
      size (int, optional): 가져올 Match Id 개수. Defaults to 30.

  Returns:
      matchIds(list): 소환사의 최근 Match Id 리스트
  """
  summonerMatches = db[col].find_one({"puuid":puuid})
  
  if not summonerMatches:
    return []
  
  else:
    summonerMatches = summonerMatches["summoner_match_ids"]
    if len(summonerMatches)<size+startIdx:
      return summonerMatches[startIdx:]
    else:
      return summonerMatches[startIdx:size+startIdx]
  
  
if __name__=="__main__":
  update("칼과 창 방패")