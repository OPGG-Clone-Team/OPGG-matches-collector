from riot_requests import summoner_v4
from error.custom_exception import DataNotExists
import datetime

# LEAGUEDATA db의 summoners만 담당
col = "summoners"

def update(db, summonerName, ignore=False, summoner_brief=None):
  # 0. summonerName 확인
  # TODO - 나중에 이부분 다시 custom 예외처리
  # if not summonerName:
  #   raise ("소환사 이름을 입력해주세요.")
  
  if not ignore:
    # 1. league_entries에서 summonerName 과 일치하는 데이터 조회
    summoner_brief = db["league_entries"].find_one({"summonerName":summonerName})
    
    # 1-1. 없다면 raise Exception
    if not summoner_brief:
      raise DataNotExists("league_entries collection에 소환사 정보가 없습니다.")
    
  # 2. summonerId를 가져와서 summoner_v4의 summoner 정보를 가져오기
  summoner = summoner_v4.getSummoner(summoner_brief["summonerId"])
  summoner["updatedAt"] = datetime.datetime.utcnow()
  summoner["queue"] = summoner_brief["queue"]
  summoner["tier"] = summoner_brief["tier"]
  summoner["rank"] = summoner_brief["rank"]
  
  # 3. db에 저장 (upsert=True)
  db[col].update_one(
      {"puuid":summoner["puuid"]},
      {"$set":summoner},
      True)
  
  print(f"소환사 {summonerName}의 정보를 성공적으로 업데이트했습니다.")
  
  return summoner

def updateAll(db):
  # 1. league_entries에 있는 소환사 정보들 중 summonerId만 가져오기"
  league_entries = list(db["league_entries"].find({}))
  
  if len(league_entries)==0:
    raise DataNotExists("league_entries collection에 소환사 정보가 없습니다.")
  
  for entry in league_entries:
    update(db, entry["summonerName"], ignore=True, summoner_brief=entry)
  
  print(f"성공적으로 {len(league_entries)}명의 소환사 정보를 업데이트했습니다.")
  return len(league_entries)

def find(db, summonerName):
  # 1. league_entries에서 summonerName 과 일치하는 데이터 조회
  summoner = db[col].find_one({"name":summonerName}, {"_id":0, "accountId":0, "id":0})
  
  if not summoner:
    return None
  
  return summoner

if __name__=="__main__":
  # 상위 경로 패키지 로드
  import sys, os
  sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
  update("Hide on bush")