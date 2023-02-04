from config.mongo import mongoClient
from riot_requests import summoner_v4
from decorator.trycatch_wrapper import trycatch
from flask import jsonify

# LEAGUEDATA db의 summoners만 담당
col = "summoners"

@trycatch
def update(app, summonerName): #app을 받아야함
  db = mongoClient(app).LEAGUEDATA
  # 1. league_entries에서 summonerName 과 일치하는 데이터 조회
  summoner_brief = db["league_entries"].find_one({"summonerName":summonerName})
  
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
  
  return summoner

@trycatch
def findSummoner(app, summonerName):
  db = mongoClient(app).LEAGUEDATA
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