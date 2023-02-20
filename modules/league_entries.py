from riot_requests import league_v4
from error.custom_exception import DataNotExists, RequestDataNotExists
from modules import summoner
from utils.date_calc import timeDifToMinute
import logging
# LEAGUEDATA db의 league_entries collection만 담당

logger = logging.getLogger("app")

col = "league_entries"

def updateAll(db):
  
  # logging.info(logging.getLevelName)
  entries = []

  entries.extend(league_v4.get_specific_league("challengerleagues"))
  entries.extend(league_v4.get_specific_league("grandmasterleagues"))
  entries.extend(league_v4.get_specific_league("masterleagues"))
  
  # 순위 정보 추가
  rank=1
  for entry in entries:
    # 2023/02/18 추가 : league_entries 넣기 전에 소환사 정보 갱신,
    #   소환사 정보가 존재하지 않거나 오래됐으면 갱신
    summonerInfo = summoner.findBySummonerId(db, entry["summonerId"])
    if not summonerInfo:
      logger.debug("DB에 소환사 정보가 조회되지 않아 업데이트합니다.")
      summonerInfo = summoner.updateBySummonerId(db, entry["summonerId"])
    else:
      logger.debug("기존 소환사 정보 유효성 검증")
      # 조회한 소환사 이름이 서로 다르고, summonerInfo의 갱신 시간이 24시간 이상 지났다면 
      # summoner update
      if summonerInfo["name"]!= entry["summonerName"]:
        logger.debug(f"소환사 이름이 서로 다릅니다.")
        timeDiff = timeDifToMinute(summonerInfo["updatedAt"]).days
        if timeDiff >= 1:
          summonerInfo = summoner.updateBySummonerId(db, entry["summonerId"])
    
    entry["rank"] = rank
    entry["summonerName"] = summonerInfo["name"]
    rank+=1
  
  logger.info('--------- 마스터 이상 소환사 정보 insert ---------')
  logger.info(f"총 소환사 수 : {len(entries)}")

  if(len(entries)==0):
    raise RequestDataNotExists("Riot Api 요청 정보가 존재하지 않습니다.")
  
  # db에 넣기 전 league_entires collection 비우기
  db[col].delete_many({})
  db[col].insert_many(entries, ordered=True)

  logger.info(f"성공적으로 {len(entries)}명의 엔트리 정보를 업데이트했습니다.")
  return len(entries)


def getSummonerBrief(db, summonerName):
  summoner = db[col].find_one({"summonerName":summonerName})
  
  if not summoner:
    raise DataNotExists("데이터베이스에서 소환사 정보를 찾을 수 없습니다.")
  
  return summoner

def find(db, page=1):
  limit = 100
  offset = (page - 1) * limit
  
  results = list(db[col].find(
      {}, {'_id': 0})
      .limit(limit).skip(offset))
  
  if len(results)==0:
    raise DataNotExists("데이터베이스에서 리그 엔트리 정보를 찾을 수 없습니다.")
  
  return results

if __name__=="__main__":
  updateAll()
    
