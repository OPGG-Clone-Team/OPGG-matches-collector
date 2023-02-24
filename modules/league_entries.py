from riot_requests import league_v4
from error.custom_exception import DataNotExists, RequestDataNotExists
from modules import summoner
from utils.date_calc import lastModifiedFromNow
import logging

logger = logging.getLogger("app")

col = "league_entries"
day = 60*60*24

def updateAll(db):
  """리그 엔트리 정보 모두 업데이트

  Args:
      db (connection)

  Raises:
      RequestDataNotExists: 요청 데이터 정보가 존재하지 않을 때

  Returns:
      lengthOfEntries(int)
  """
  entries = []

  entries.extend(league_v4.get_specific_league("challengerleagues"))
  entries.extend(league_v4.get_specific_league("grandmasterleagues"))
  entries.extend(league_v4.get_specific_league("masterleagues"))

  rank = 1 # 순위 정보 추가
  for entry in entries:
    entry["rank"] = rank
    summoner_info = summoner.findBySummonerId(db, entry["summonerId"])
    
    if not summoner_info: # 소환사 정보가 존재하지 않으면 업데이트
      logger.info("DB에 소환사 정보가 조회되지 않아 업데이트합니다.")
      summoner_info = summoner.updateBySummonerBrief(db, entry)
    
    else: # 조회한 소환사 이름이 서로 다르고, summonerInfo의 갱신 시간이 24시간 이상 지났다면 summoner update
      if summoner_info["name"] != entry["summonerName"] \
        and lastModifiedFromNow(summoner_info["updatedAt"], utc=False).seconds >= day:
        logger.info("리그 엔트리 소환사명 : %s, summoners collection 소환사명 : %s",
                    entry["summonerName"], summoner_info["name"])
        summoner_info = summoner.updateBySummonerBrief(db, entry)

    entry["summonerName"] = summoner_info["name"]
    rank += 1

  logger.info('--------- 마스터 이상 소환사 정보 insert ---------')
  logger.info(f"총 소환사 수 : {len(entries)}")

  if len(entries) == 0:
    raise RequestDataNotExists("Riot Api 요청 정보가 존재하지 않습니다.")

  db[col].delete_many({}) # db에 넣기 전 league_entires collection 비우기
  db[col].insert_many(entries, ordered=True)

  logger.info(f"성공적으로 {len(entries)}명의 엔트리 정보를 업데이트했습니다.")
  return len(entries)

def getSummonerBrief(db, summonerName):
  """특정 소환사 정보 League Entry에서 조회

  Args:
      db (connection)
      summonerName (str)

  Raises:
      DataNotExists

  Returns:
      summoner_brief: league_entry row
  """
  summoner_brief = db[col].find_one({"summonerName": summonerName})

  if not summoner_brief:
    raise DataNotExists("DB에서 소환사 정보를 찾을 수 없습니다.")

  return summoner_brief


def find(db, page=1):
  """랭킹정보 페이지 단위로 조회

  Args:
      db (connection)
      page (int, optional): 가져올 랭킹정보 페이지 정보. Defaults to 1.

  Raises:
      DataNotExists

  Returns:
      [entries]
  """
  limit = 100
  offset = (page - 1) * limit

  results = list(db[col].find(
      {}, {'_id': 0})
      .limit(limit).skip(offset))

  if len(results) == 0:
    raise DataNotExists("데이터베이스에서 리그 엔트리 정보를 찾을 수 없습니다.")

  return results
