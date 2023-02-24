from riot_requests import summoner_v4
from error.custom_exception import TooManySummonerRequest, DataNotExists
import datetime
import logging
from utils.date_calc import lastModifiedFromNow
from modules import league_entries

logger = logging.getLogger("app")
col = "summoners"

def updateBySummonerName(db, summonerName):
  """소환사 이름으로 소환사 정보 업데이트
  업데이트 최종 시각이 현재 시간과 2분 이하로 차이나면 업데이트 하지 않고 예외 발생

  Args:
      db (connection)
      summonerName (str)

  Raises:
      DataNotExists
      TooManySummonerRequest: 업데이트 최종 시각이 현재 시간과 2분 이하로 차이날 때

  Returns:
      summoner: 소환사 정보
  """
  # 0. DB에서 leagueEntry에 summoner 정보가 있는지 확인, 없으면 예외발생
  summoner_brief = league_entries.getSummonerBrief(db, summonerName)
  if not summoner_brief:
    raise DataNotExists("DB 엔트리 정보에 소환사가 존재하지 않습니다.")

  # 1. DB에서 summonerInfo 조회
  summoner_info = findBySummonerName(db, summonerName)

  # 2. 조회 결과가 없으면 그냥 업데이트
  if not summoner_info:
    summoner = summoner_v4.requestSummonerByName(summonerName)
  else:
    # 2-1. 조회 후 updatedAt 시각이 2분이 지나지 않았으면 에러 발생시키기
    timeDiff = lastModifiedFromNow(summoner_info["updatedAt"]).seconds
    if timeDiff < 60*2:
      raise TooManySummonerRequest(f"{timeDiff}초 전에 이미 소환사 정보를 갱신했습니다.")

  # 2-2. summonerId를 가져와서 summoner_v4로 소환사 정보 업데이트
  summoner = summoner_v4.requestSummonerByName(summonerName)

  addSummonerField(summoner, summoner_brief)

  # 3. db에 저장 (upsert=True)
  db[col].update_one(
      {"puuid": summoner["puuid"]},
      {"$set": summoner},
      True)

  logger.info(f"소환사 {summonerName}의 정보를 성공적으로 업데이트했습니다.")

  # 저장된 정보는 utc time이기 때문에 9시간 더해서 보여주기
  summoner["updatedAt"] = summoner["updatedAt"]+datetime.timedelta(hours=9)
  return summoner

def updateBySummonerBrief(db, summoner_brief):
  """league_entries의 entry 정보로 소환사 업데이트\n
  league_entries에서 updateAll 호출 시에만 동작, updateAt 정보를 확인하지 않음
  
  Args:
      db (connection)
      summoner_brief (entry)

  Raises:
      AttributeError: 잘못된 함수 인자 사용

  Returns:
      summoner
  """
  if not summoner_brief:
    raise AttributeError(f"{__name__}의 인자를 잘못 넘겼습니다.")

  summoner = summoner_v4.requestSummonerById(summoner_brief["summonerId"])

  addSummonerField(summoner, summoner_brief)

  # 3. db에 저장 (upsert=True)
  db[col].update_one(
      {"puuid": summoner["puuid"]},
      {"$set": summoner},
      True)

  summonerName = summoner["name"]

  logger.info(f"소환사 {summonerName}의 정보를 성공적으로 업데이트했습니다.")

  summoner["updatedAt"] = summoner["updatedAt"]+datetime.timedelta(hours=9)
  return summoner


def findBySummonerName(db, summonerName):
  """소환사 이름으로 소환사 정보 조회

  Args:
      db (connection)
      summonerName (str)

  Returns:
      summoner
  """
  summoner = db[col].find_one(
    {"name": summonerName}, 
    {"_id": 0, "accountId": 0})

  if not summoner:
    return None

  summoner["updatedAt"] = summoner["updatedAt"]+datetime.timedelta(hours=9)
  return summoner


def findBySummonerId(db, summonerId):
  """소환사 ID로 소환사 정보 조회

  Args:
      db (connection)
      summonerId (str)

  Returns:
      summoner
  """
  summoner = db["summoners"].find_one(
    {'id': summonerId},
    {"_id": 0, "accountId": 0})

  if not summoner:
    return None

  summoner["updatedAt"] = summoner["updatedAt"]+datetime.timedelta(hours=9)
  return summoner


def addSummonerField(summoner, summoner_brief):
  """summoner 객체에 랭크 정보 필드 추가

  Args:
      summoner 
      summoner_brief
  """
  
  summoner["updatedAt"] = datetime.datetime.utcnow()
  summoner["queue"] = summoner_brief["queue"]
  summoner["tier"] = summoner_brief["tier"]
  summoner["rank"] = summoner_brief["rank"]
